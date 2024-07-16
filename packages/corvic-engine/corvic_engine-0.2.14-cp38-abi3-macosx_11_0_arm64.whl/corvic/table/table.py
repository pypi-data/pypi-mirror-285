"""Table."""

from __future__ import annotations

import dataclasses
import functools
from collections.abc import Iterable, Mapping, Sequence
from typing import (
    Any,
    Final,
    Literal,
    Protocol,
    TypeAlias,
    TypeVar,
    cast,
)

import more_itertools
import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq
import structlog
from typing_extensions import Self

from corvic import op_graph
from corvic.op_graph import Schema
from corvic.result import BadArgumentError, Error, NotFoundError, Ok
from corvic.system import (
    Client,
    DataMisplacedError,
    ExecutionContext,
    TableComputeContext,
)

MetadataValue: TypeAlias = (
    "None | bool | str | float | dict[str, MetadataValue] | list[MetadataValue]"
)


class TypedMetadata(Protocol):
    """Metadata types implement this to participate in the typed lookup protocol."""

    @classmethod
    def metadata_key(cls) -> str: ...

    @classmethod
    def from_value(cls, value: MetadataValue) -> Self: ...

    def to_value(self) -> MetadataValue: ...


_TM = TypeVar("_TM", bound=TypedMetadata)


_logger = structlog.get_logger()


@dataclasses.dataclass
class DataclassAsTypedMetadataMixin:
    """A TypedMetadata mixin for dataclasses.

    Inheriting from this mixin adds the methods necessary for implementing
    the TypedMetadata protocol. Each implementer must choose their own unique
    MEATADATA_KEY.

    NOTE: Removing fields, changing the name of fields, or adding new fields
    that do not have default values will cause exceptions when reading old
    serialized data.

    Example Usage:
    >>> @dataclass
    >>> ModuleSpecificMetadata(DataclassAsTypedMetadataMixin):
    >>>     @classmethod
    >>>     def metadata_key(cls):
    >>>         return "unique-metadata-name"
    >>>     string_value: str
    >>>     ...
    """

    @classmethod
    def from_value(cls, value: MetadataValue):
        if not isinstance(value, dict):
            raise BadArgumentError("expected dict value")

        return cls(**value)

    def to_value(self) -> MetadataValue:
        return dataclasses.asdict(self)


class NotReadyError(Error):
    """NotReadyError result Error.

    Raised when the result depends on some action that is expected to
    complete eventually.
    """


class Table:
    """Table that computed or loaded from storage when needed.

    Table objects are a little different in that they are constructed (e.g., in memory)
    before they are registered. A table that is not registered is an "anonymous" table.
    Anonymous tables have no ID (Table.id returns the empty string) and cannot be found
    by table client instances.
    """

    MAX_ROWS_PER_SLICE: Final = 4096

    _client: Client
    _op: Final[op_graph.Op]
    _staged: bool

    def __init__(
        self,
        client: Client,
        op: op_graph.Op,
    ):
        self._client = client
        self._op = op
        self._staged = False

    def __eq__(self, other: object):
        if not isinstance(other, type(self)):
            return False
        return self._op == other._op

    @property
    def client(self):
        return self._client

    @property
    def op_graph(self):
        return self._op

    def _must_wait_for_staging(self) -> Ok[None] | NotReadyError:
        if self.data_staging_complete():
            return Ok(None)
        return NotReadyError("waiting for system to materialize staging data")

    @classmethod
    def _compute_num_rows(cls, op: op_graph.Op) -> int | None:  # noqa: PLR0911
        match op:
            case op_graph.op.SelectFromStaging() | op_graph.op.ReadFromParquet():
                return op.expected_rows
            case (
                op_graph.op.SelectColumns()
                | op_graph.op.RenameColumns()
                | op_graph.op.UpdateMetadata()
                | op_graph.op.SetMetadata()
                | op_graph.op.RemoveFromMetadata()
                | op_graph.op.UpdateFeatureTypes()
                | op_graph.op.UnnestStruct()
                | op_graph.op.AddLiteralColumn()
                | op_graph.op.CombineColumns()
                | op_graph.op.EmbedColumn()
                | op_graph.op.NestIntoStruct()
            ):
                return cls._compute_num_rows(op.source)
            case op_graph.op.LimitRows():
                source_rows = cls._compute_num_rows(op.source)
                return min(op.num_rows, source_rows) if source_rows else None
            case op_graph.op.Empty():
                return 0
            case op_graph.op.SelectFromVectorStaging():
                return op.num_results
            case op_graph.op.Concat():
                source_row_counts = (cls._compute_num_rows(src) for src in op.tables)
                rows = 0
                for count in source_row_counts:
                    if count is None:
                        return None
                    rows += count
                return rows
            case (
                op_graph.op.Join()
                | op_graph.op.RollupByAggregation()
                | op_graph.op.OrderBy()
                | op_graph.op.FilterRows()
                | op_graph.op.DistinctRows()
                | op_graph.op.EmbedNode2vecFromEdgeLists()
                | op_graph.op.EmbeddingMetrics()
                | op_graph.op.EmbeddingCoordinates()
            ):
                return None

    @classmethod
    def _compute_metadata(cls, op: op_graph.Op) -> dict[str, Any]:
        match op:
            case op_graph.op.SetMetadata():
                return dict(op.new_metadata)

            case op_graph.op.UpdateMetadata():
                source_metadata = cls._compute_metadata(op.source)
                source_metadata.update(op.metadata_updates)
                return source_metadata

            case op_graph.op.RemoveFromMetadata():
                source_metadata = cls._compute_metadata(op.source)
                for key in op.keys_to_remove:
                    source_metadata.pop(key, None)
                return source_metadata

            case op_graph.op.Join():
                source_metadata = cls._compute_metadata(op.right_source)
                # for join, left source takes precedence in terms
                # of column names, ditto that for metadata names
                source_metadata.update(cls._compute_metadata(op.left_source))
                return source_metadata

            case (
                op_graph.op.SelectColumns()
                | op_graph.op.RenameColumns()
                | op_graph.op.LimitRows()
                | op_graph.op.OrderBy()
                | op_graph.op.FilterRows()
                | op_graph.op.UpdateFeatureTypes()
                | op_graph.op.RollupByAggregation()
                | op_graph.op.DistinctRows()
                | op_graph.op.EmbedNode2vecFromEdgeLists()
                | op_graph.op.SelectFromStaging()
                | op_graph.op.Empty()
                | op_graph.op.EmbeddingMetrics()
                | op_graph.op.EmbeddingCoordinates()
                | op_graph.op.ReadFromParquet()
                | op_graph.op.SelectFromVectorStaging()
                | op_graph.op.Concat()
                | op_graph.op.UnnestStruct()
                | op_graph.op.NestIntoStruct()
                | op_graph.op.AddLiteralColumn()
                | op_graph.op.CombineColumns()
                | op_graph.op.EmbedColumn()
            ):
                metadata = dict[str, Any]()
                for source in op.sources():
                    metadata.update(cls._compute_metadata(source))
                return metadata

    @functools.cached_property
    def num_rows(self):
        return self._compute_num_rows(self.op_graph)

    @functools.cached_property
    def schema(self) -> Schema:
        return self.op_graph.schema

    @functools.cached_property
    def metadata(self) -> Mapping[str, Any]:
        return self._compute_metadata(self.op_graph)

    @classmethod
    def from_ops(cls, client: Client, op: op_graph.Op):
        return cls(client, op=op)

    @classmethod
    def from_bytes(cls, client: Client, op: bytes):
        return cls.from_ops(client, op_graph.op.from_bytes(op))

    @classmethod
    def from_parquet_file(
        cls,
        client: Client,
        url: str,
    ) -> Ok[Table] | DataMisplacedError | BadArgumentError:
        """Build a table from an arrow Table."""
        blob = client.storage_manager.blob_from_url(url)
        with blob.open("rb") as stream:
            metadata = pq.read_metadata(stream)
        num_rows = metadata.num_rows
        arrow_schema = metadata.schema.to_arrow_schema()
        schema = Schema.from_arrow(arrow_schema)
        case_insensitive_schema = {column.name.upper() for column in schema}
        if len(schema) != len(case_insensitive_schema):
            return BadArgumentError(
                "column names are case insensitive and must be unique"
            )
        null_columns: list[str] = []
        kept_columns: list[str] = []
        for column in schema:
            if pa.types.is_null(column.dtype):
                null_columns.append(column.name)
            else:
                kept_columns.append(column.name)
        if len(null_columns) > 0:
            _logger.warning("dropped null columns", columns=null_columns)

        match client.storage_manager.tabular.blob_name_from_url(url):
            case Ok(table_name):
                op = op_graph.from_staging(
                    blob_names=[table_name],
                    arrow_schema=schema.to_arrow(),
                    feature_types=[field.ftype for field in schema],
                    expected_rows=num_rows,
                )
            case DataMisplacedError() as error:
                return error
        if len(null_columns) > 0:
            op = op.select_columns(kept_columns)
        return Ok(cls.from_ops(client, op))

    def to_bytes(self):
        return self.op_graph.to_bytes()

    def to_polars(
        self, *, flatten_single_field: bool = False
    ) -> Ok[Iterable[pl.DataFrame]] | NotReadyError | BadArgumentError:
        """Stream over the view as a series of Polars DataFrames."""
        match self.to_batches():
            case Ok(batch_reader):
                pass
            case NotReadyError() | BadArgumentError() as error:
                return error
        empty_table = cast(
            pl.DataFrame, pl.from_arrow(self.schema.to_arrow().empty_table())
        )
        polars_schema = empty_table.schema

        def generator():
            some = False
            for batch in batch_reader:
                df_batch = cast(
                    pl.DataFrame,
                    pl.from_arrow(batch, rechunk=False, schema_overrides=polars_schema),
                ).select(key for key in polars_schema)

                some = True
                yield df_batch
            if not some:
                yield empty_table

        return Ok(generator())

    def _staging_op_satisfied(self, staging_op: op_graph.op.SelectFromStaging) -> bool:
        result = self.client.staging_db.count_ingested_rows(*staging_op.blob_names)
        if result < staging_op.expected_rows:
            return False

        if result == staging_op.expected_rows:
            return True

        raise Error(
            "table materialized more rows than expected",
            blob_names=staging_op.blob_names,
            expected_row_count=staging_op.expected_rows,
            actual_row_count=result,
        )

    def data_staging_complete(self) -> bool:
        """True if the data this table depends on has been staged."""
        if self._staged:
            return True

        # TODO(thunt): The obvious optimization here is to issue these queries together
        # and overlap the wait time.
        staged = all(
            self._staging_op_satisfied(staging_op)
            for staging_op in self._get_staging_ops(self.op_graph)
        )

        if staged:
            self._staged = True

        return staged

    @classmethod
    def _get_staging_ops(
        cls, op: op_graph.Op
    ) -> Iterable[op_graph.op.SelectFromStaging]:
        match op:
            case op_graph.op.SelectFromStaging():
                return [op]
            case _:
                return more_itertools.flatten(map(cls._get_staging_ops, op.sources()))

    def head(self) -> Table:
        """Get up to the first 10 rows of the table."""
        return Table(
            self.client,
            self.op_graph.limit_rows(num_rows=10),
        )

    def distinct_rows(self) -> Table:
        return Table(
            self.client,
            self.op_graph.distinct_rows(),
        )

    def order_by(self, columns: Sequence[str], *, desc: bool) -> Table:
        return Table(
            self.client,
            self.op_graph.order_by(columns=columns, desc=desc),
        )

    def update_feature_types(
        self, new_feature_types: Mapping[str, op_graph.FeatureType]
    ) -> Table:
        return Table(
            self.client,
            self.op_graph.update_feature_types(new_feature_types=new_feature_types),
        )

    def to_batches(self) -> Ok[pa.RecordBatchReader] | NotReadyError | BadArgumentError:
        """Convert every row to a dictionary of Python-native values."""
        match self._must_wait_for_staging():
            case Ok():
                context = ExecutionContext(
                    tables_to_compute=[
                        TableComputeContext(
                            self.op_graph,
                            output_url_prefix=self.client.storage_manager.space_run.make_anonymous_table_url(),
                        )
                    ],
                )
                return self.client.executor.execute(context).map(
                    lambda result: result.tables[0].to_batch_reader()
                )
            case NotReadyError() as err:
                return err

    @staticmethod
    def _resolve_conflicting_column_names(
        left_schema: Schema,
        right_schema: Schema,
        conflict_suffix: str,
        right_join_columns: list[str] | str,
        right_op_graph: op_graph.Op,
    ) -> op_graph.Op:
        """Returns the new schema the right table op_graph.

        The new schema will be returned with any necessary renames applied.
        """
        if isinstance(right_join_columns, str):
            right_join_columns = [right_join_columns]
        new_fields = {field.name: field for field in left_schema}
        right_table_renames: dict[str, str] = {}
        for field in right_schema:
            if field.name in right_join_columns:
                continue
            if field.name in new_fields:
                new_field = field.rename(f"{field.name}{conflict_suffix}")
                new_fields[new_field.name] = new_field
                right_table_renames[field.name] = new_field.name
            else:
                new_fields[field.name] = field

        if right_table_renames:
            right_op_graph = right_op_graph.rename_columns(right_table_renames)

        return right_op_graph

    def rename_columns(self, old_to_new: Mapping[str, str]) -> Table:
        old_to_new = {
            old_name: new_name
            for old_name, new_name in old_to_new.items()
            if old_name != new_name
        }
        if not old_to_new:
            return self

        return Table(self.client, self.op_graph.rename_columns(old_to_new))

    def join(
        self,
        right_table: Table,
        *,
        left_on: str | list[str],
        right_on: str | list[str],
        how: Literal["inner", "left outer"] = "left outer",
        suffix: str | None = None,
    ) -> Table:
        """Join this Table with another.

        If suffix is not provided, other_table.name is appended to the name of columns
        in other_table that conflict with column names in this table.
        """
        suffix = suffix or "_right"
        right_log = self._resolve_conflicting_column_names(
            self.schema,
            right_table.schema,
            right_join_columns=right_on,
            conflict_suffix=suffix,
            right_op_graph=right_table.op_graph,
        )

        return Table(
            self.client,
            op=self.op_graph.join(
                right_log,
                left_on=left_on,
                right_on=right_on,
                how=how,
            ),
        )

    def has_typed_metadata(self, typed_metadata: type[TypedMetadata]) -> bool:
        return typed_metadata.metadata_key() in self.metadata

    def get_typed_metadata(self, typed_metadata: type[_TM]) -> _TM:
        if not self.has_typed_metadata(typed_metadata):
            raise NotFoundError("typed metadata key was not set")
        value = self.metadata[typed_metadata.metadata_key()]
        return typed_metadata.from_value(value)

    def update_typed_metadata(self, *typed_metadatas: TypedMetadata):
        return self.update_metadata(
            {
                typed_metadata.metadata_key(): typed_metadata.to_value()
                for typed_metadata in typed_metadatas
            }
        )

    def update_metadata(self, metadata_updates: Mapping[str, Any]):
        if not metadata_updates:
            return self
        return Table(self.client, op=self.op_graph.update_metadata(metadata_updates))

    def set_metadata(self, new_metadata: Mapping[str, Any]):
        """Drop the old metadata and overwrite it with new_metadata."""
        return Table(self.client, op=self.op_graph.set_metadata(new_metadata))

    def remove_from_metadata(self, keys_to_remove: Sequence[str]) -> Table:
        """Remove the listed keys from the metadata if they exist."""
        if isinstance(keys_to_remove, str):
            keys_to_remove = [keys_to_remove]
        keys_to_remove = [key for key in keys_to_remove if key in self.metadata]
        if not keys_to_remove:
            return self
        return Table(self.client, op=self.op_graph.remove_from_metadata(keys_to_remove))

    def select(self, columns_to_select: Sequence[str]) -> Table:
        """Return a table with only the columns listed."""
        return Table(
            self.client, op=self.op_graph.select_columns(columns=columns_to_select)
        )

    def without_columns(
        self,
        columns_to_remove: Iterable[str],
    ) -> Table:
        """Return a table without the columns listed."""
        raise NotImplementedError()

    def rollup(
        self,
        *,
        group_by: str | list[str],
        target: str,
        agg: Literal["count", "avg", "mode", "min", "max", "sum"],
    ) -> Table:
        """Apply a basic rollup.

        The new column's name is computed from the target's name and the computation
        applied.
        """
        return Table(
            self.client,
            op=self.op_graph.rollup_by_aggregation(
                group_by=group_by,
                target=target,
                aggregation=agg,
            ),
        )

    def _ensure_filter_columns_exist(self, row_filter: op_graph.RowFilter):
        match row_filter:
            case op_graph.row_filter.CombineFilters():
                for filter_ in row_filter.row_filters:
                    self._ensure_filter_columns_exist(filter_)
            case op_graph.row_filter.CompareColumnToLiteral():
                if not self.schema.has_column(row_filter.column_name):
                    raise BadArgumentError(
                        "column in filter does not exist in the table",
                        column_name=row_filter.column_name,
                    )

    def filter_rows(self, row_filter: op_graph.RowFilter):
        self._ensure_filter_columns_exist(row_filter)
        return Table(self.client, op=self.op_graph.filter_rows(row_filter))

    def embed_text(
        self,
        *,
        target: str,
        model_name: str,
    ) -> Table:
        """Produce a table with new embedding column.

        The new column's name is computed from the target's name and the
        computation applied.
        """
        raise NotImplementedError()
