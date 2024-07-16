"""Staging-agnostic in-memory executor."""

from __future__ import annotations

import dataclasses
import functools
from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any, Final, cast

import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq
import structlog
from google.protobuf import json_format, struct_pb2

from corvic import embed, op_graph, sql
from corvic.lazy_import import lazy_import
from corvic.result import BadArgumentError, InternalError, Ok
from corvic.system._embedder import EmbedTextContext, TextEmbedder
from corvic.system.op_graph_executor import (
    ExecutionContext,
    ExecutionResult,
    OpGraphExecutor,
    TableComputeContext,
    TableComputeResult,
    TableSliceArgs,
)
from corvic.system.staging import StagingDB
from corvic.system.storage import StorageManager
from corvic_generated.orm.v1 import table_pb2

_logger = structlog.get_logger()

if TYPE_CHECKING:
    from corvic import embedding_metric
else:
    embedding_metric = lazy_import("corvic.embedding_metric")


_MIN_EMBEDDINGS_FOR_EMBEDDINGS_SUMMARY: Final = 3


def batch_to_proto_struct(batch: pa.RecordBatch) -> list[struct_pb2.Struct]:
    """Converts a RecordBatch to protobuf Structs safely."""
    data = batch.to_pylist()
    structs = [struct_pb2.Struct() for _ in range(len(data))]
    for idx, datum in enumerate(data):
        make_dict_bytes_human_readable(datum)
        json_format.ParseDict(datum, structs[idx])
    return structs


def cast_record_batch(batch: pa.RecordBatch, new_schema: pa.Schema) -> pa.RecordBatch:
    """Casts a RecordBatch to a new schema safely."""
    select = batch.select(new_schema.names)
    merged_schema = _merge_new_schema(new_schema, select.schema)
    return select.cast(merged_schema, safe=True)


def make_list_bytes_human_readable(data: list[Any]) -> None:
    """Utility function to cleanup list data types.

    This function ensures that the list can be converted to
    a protobuf Value safely.
    """
    for i in range(len(data)):
        if isinstance(data[i], bytes):
            data[i] = data[i].decode("utf-8", errors="ignore")
        elif isinstance(data[i], dict):
            make_dict_bytes_human_readable(data[i])
        elif isinstance(data[i], list):
            make_list_bytes_human_readable(data[i])


def make_dict_bytes_human_readable(data: MutableMapping[str, Any]) -> None:
    """Utility function to cleanup mapping data types.

    This function ensures that the mapping can be converted to
    a protobuf Value safely.
    """
    for k, v in data.items():
        if isinstance(v, bytes):
            data[k] = v.decode("utf-8", errors="ignore")
        elif isinstance(v, dict):
            make_dict_bytes_human_readable(data[k])
        elif isinstance(v, list):
            make_list_bytes_human_readable(data[k])


def _merge_new_schema(new_schema: pa.Schema, old_schema: pa.Schema) -> pa.Schema:
    """Merges a new arrow Schema with the old schema for use before casting data.

    This merge explicitly avoids casting a non-null column to null,
    which is never a valid cast.
    """
    # TODO(Patrick): handle maps, etc
    patched_schema: list[pa.Field] = []
    for field in new_schema:
        old_field = old_schema.field(field.name)
        if pa.types.is_struct(field.type):
            patched_schema.append(_patch_struct_field(field, old_field))
        elif pa.types.is_list(field.type) or pa.types.is_large_list(field.type):
            patched_schema.append(_patch_list_field(field, old_field))
        elif not pa.types.is_null(field.type):
            patched_schema.append(field)
        elif old_field and not pa.types.is_null(old_field.type):
            patched_schema.append(field.with_type(old_field.type))
        else:
            patched_schema.append(field)
    return pa.schema(patched_schema, new_schema.metadata)


def _wrap_list_type(
    list_type: pa.ListType | pa.LargeListType, list_value_field: pa.Field
) -> pa.DataType:
    if isinstance(list_type, pa.ListType):
        return pa.list_(value_type=list_value_field)
    return pa.large_list(value_type=list_value_field)


def _patch_list_field(
    new_field: pa.Field,
    old_field: pa.Field,
) -> pa.Field:
    new_field_type = new_field.type
    old_field_type = old_field.type
    if (
        not old_field
        or (
            not isinstance(new_field_type, pa.ListType)
            and not isinstance(new_field_type, pa.LargeListType)
        )
        or (
            not isinstance(old_field_type, pa.ListType)
            and not isinstance(old_field_type, pa.LargeListType)
        )
    ):
        return new_field
    new_list_field = new_field_type.value_field
    old_list_type = old_field_type.value_field.type

    if pa.types.is_struct(new_list_field.type):
        return new_field.with_type(
            _wrap_list_type(
                new_field_type,
                new_field_type.value_field.with_type(
                    _patch_struct_field(
                        new_list_field, new_list_field.with_type(old_list_type)
                    ).type
                ),
            )
        )
    if pa.types.is_list(new_list_field.type) or pa.types.is_large_list(
        new_list_field.type
    ):
        return new_field.with_type(
            _wrap_list_type(
                new_field_type,
                new_field_type.value_field.with_type(
                    _patch_list_field(
                        new_list_field, new_list_field.with_type(old_list_type)
                    ).type
                ),
            )
        )
    if not pa.types.is_null(new_list_field.type):
        return new_field
    return new_field.with_type(
        _wrap_list_type(new_field_type, old_field_type.value_field)
    )


def _patch_struct_field(
    new_field: pa.Field,
    old_field: pa.Field,
) -> pa.Field:
    new_field_type = new_field.type
    if not old_field or not isinstance(new_field_type, pa.StructType):
        return new_field
    old_struct = old_field.type
    if not isinstance(old_struct, pa.StructType):
        return new_field

    patched_nested_fields: list[pa.Field] = []
    for field_index in range(old_struct.num_fields):
        old_nested_field = old_struct.field(field_index)
        field = new_field_type.field(
            new_field_type.get_field_index(old_nested_field.name)
        )
        if pa.types.is_struct(field.type):
            patched_nested_fields.append(
                _patch_struct_field(field, field.with_type(old_nested_field.type))
            )
        elif pa.types.is_list(field.type) or pa.types.is_large_list(field.type):
            patched_nested_fields.append(
                _patch_list_field(field, field.with_type(old_nested_field.type))
            )
        elif not pa.types.is_null(field.type):
            patched_nested_fields.append(field)
        elif old_nested_field.type and not pa.types.is_null(old_nested_field.type):
            patched_nested_fields.append(field.with_type(old_nested_field.type))
        else:
            patched_nested_fields.append(field)
    return new_field.with_type(pa.struct(patched_nested_fields))


def _as_df(
    batch_or_batch_container: pa.RecordBatchReader | pa.RecordBatch | _SchemaAndBatches,
):
    empty_dataframe = cast(
        pl.DataFrame, pl.from_arrow(batch_or_batch_container.schema.empty_table())
    )
    match batch_or_batch_container:
        case pa.RecordBatchReader():
            batches = list(batch_or_batch_container)
        case _SchemaAndBatches():
            batches = batch_or_batch_container.batches
        case pa.RecordBatch():
            batches = [batch_or_batch_container]

    if not batches:
        return empty_dataframe

    return cast(
        pl.DataFrame,
        pl.from_arrow(batches, rechunk=False, schema=empty_dataframe.schema),
    )


def _patch_batch_reader_schema(
    original_reader: pa.RecordBatchReader,
    new_schema: pa.Schema,
    metrics: dict[str, Any],
) -> _SchemaAndBatches:
    def new_batches():
        for batch in original_reader:
            yield cast_record_batch(batch, new_schema)

    return _SchemaAndBatches(
        schema=new_schema, batches=list(new_batches()), metrics=metrics
    )


@dataclasses.dataclass(frozen=True)
class _SchemaAndBatches:
    schema: pa.Schema
    batches: list[pa.RecordBatch]
    metrics: dict[str, Any]

    def to_batch_reader(self):
        return pa.RecordBatchReader.from_batches(
            schema=self.schema, batches=self.batches
        )

    @classmethod
    def from_dataframe(cls, dataframe: pl.DataFrame, metrics: dict[str, Any]):
        table = dataframe.to_arrow()
        schema = table.schema
        return cls(schema, table.to_batches(), metrics)


@dataclasses.dataclass(frozen=True)
class _SlicedTable:
    op_graph: op_graph.Op
    slice_args: TableSliceArgs | None


@dataclasses.dataclass
class _InMemoryExecutionContext:
    exec_context: ExecutionContext
    current_output_context: TableComputeContext | None = None

    # Using _SchemaAndBatches rather than a RecordBatchReader since the latter's
    # contract only guarantees one iteration and these might be accessed more than
    # once
    computed_batches_for_op_graph: dict[_SlicedTable, _SchemaAndBatches] = (
        dataclasses.field(default_factory=dict)
    )

    @classmethod
    def count_source_op_uses(
        cls,
        op: op_graph.Op,
        use_counts: dict[_SlicedTable, int],
        slice_args: TableSliceArgs | None,
    ):
        for source in op.sources():
            sliced_table = _SlicedTable(source, slice_args)
            use_counts[sliced_table] = use_counts.get(sliced_table, 0) + 1
            cls.count_source_op_uses(source, use_counts, slice_args)

    @property
    def current_slice_args(self) -> TableSliceArgs | None:
        if self.current_output_context:
            return self.current_output_context.sql_output_slice_args
        return None

    @functools.cached_property
    def reused_tables(self) -> set[_SlicedTable]:
        use_counts = dict[_SlicedTable, int]()
        for output_table in self.output_tables:
            self.count_source_op_uses(
                output_table.op_graph, use_counts, output_table.slice_args
            )

        return {op for op, count in use_counts.items() if count > 1}

    @functools.cached_property
    def output_tables(self) -> set[_SlicedTable]:
        return {
            _SlicedTable(ctx.table_op_graph, ctx.sql_output_slice_args)
            for ctx in self.exec_context.tables_to_compute
        }


class InMemoryTableComputeResult(TableComputeResult):
    """The in-memory result of computing a particular op graph."""

    def __init__(
        self,
        storage_manager: StorageManager,
        batches: _SchemaAndBatches,
        context: TableComputeContext,
    ):
        self._storage_manager = storage_manager
        self._batches = batches
        self._context = context

    @property
    def metrics(self):
        return self._batches.metrics

    def to_batch_reader(self) -> pa.RecordBatchReader:
        return self._batches.to_batch_reader()

    def to_urls(self) -> list[str]:
        # one file for now; we may produce more in the future
        file_idx = 0
        file_name = f"{self._context.output_url_prefix}.{file_idx:>06}"
        with (
            self._storage_manager.blob_from_url(file_name).open("wb") as stream,
            pq.ParquetWriter(stream, self._batches.schema) as writer,
        ):
            for batch in self._batches.batches:
                writer.write_batch(batch)

        return [file_name]

    @property
    def context(self) -> TableComputeContext:
        return self._context


class InMemoryExecutionResult(ExecutionResult):
    """A container for in-memory results.

    This container is optimized to avoid writes to disk, i.e., `to_batch_reader` will
    be fast `to_urls` will be slow.
    """

    def __init__(
        self,
        tables: list[InMemoryTableComputeResult],
        context: ExecutionContext,
    ):
        self._tables = tables
        self._context = context

    @classmethod
    def make(
        cls,
        storage_manager: StorageManager,
        in_memory_context: _InMemoryExecutionContext,
        context: ExecutionContext,
    ) -> InMemoryExecutionResult:
        tables = [
            InMemoryTableComputeResult(
                storage_manager,
                in_memory_context.computed_batches_for_op_graph[
                    _SlicedTable(
                        table_context.table_op_graph,
                        table_context.sql_output_slice_args,
                    )
                ],
                table_context,
            )
            for table_context in context.tables_to_compute
        ]
        return InMemoryExecutionResult(
            tables,
            context,
        )

    @property
    def tables(self) -> list[InMemoryTableComputeResult]:
        return self._tables

    @property
    def context(self) -> ExecutionContext:
        return self._context


class InMemoryExecutor(OpGraphExecutor):
    """Executes op_graphs in memory (after staging queries)."""

    def __init__(
        self,
        staging_db: StagingDB,
        storage_manager: StorageManager,
        text_embedder: TextEmbedder,
    ):
        self._staging_db = staging_db
        self._storage_manager = storage_manager
        self._text_embedder = text_embedder

    @classmethod
    def _is_sql_compatible(cls, op: op_graph.Op) -> bool:
        return isinstance(op, sql.SqlComputableOp) and all(
            cls._is_sql_compatible(sub_op) for sub_op in op.sources()
        )

    def _execute_read_from_parquet(
        self, op: op_graph.op.ReadFromParquet, context: _InMemoryExecutionContext
    ) -> _SchemaAndBatches:
        batches: list[pa.RecordBatch] = []
        for blob_name in op.blob_names:
            with (
                self._storage_manager.blob_from_url(blob_name).open("rb") as stream,
            ):
                batches.extend(
                    # reading files with pyarrow, then converting them to polars
                    # can cause "ShapeError" bugs. That's why we're not reading this
                    # using pyarrow.
                    pl.read_parquet(
                        source=stream,
                        columns=op.arrow_schema.names,
                        use_pyarrow=False,
                    )
                    .to_arrow()
                    .to_batches()
                )
        return _SchemaAndBatches(op.arrow_schema, batches=batches, metrics={})

    def _execute_rollup_by_aggregation(
        self, op: op_graph.op.RollupByAggregation, context: _InMemoryExecutionContext
    ) -> _SchemaAndBatches:
        raise NotImplementedError(
            "rollup by aggregation outside of sql not implemented"
        )

    def _execute_rename_columns(
        self, op: op_graph.op.RenameColumns, context: _InMemoryExecutionContext
    ) -> _SchemaAndBatches:
        source_batches = self._execute(op.source, context)
        return _SchemaAndBatches.from_dataframe(
            _as_df(source_batches).rename(dict(op.old_name_to_new)),
            source_batches.metrics,
        )

    def _execute_select_columns(
        self, op: op_graph.op.SelectColumns, context: _InMemoryExecutionContext
    ):
        source_batches = self._execute(op.source, context)
        return _SchemaAndBatches.from_dataframe(
            _as_df(source_batches).select(op.columns), source_batches.metrics
        )

    def _execute_limit_rows(
        self, op: op_graph.op.LimitRows, context: _InMemoryExecutionContext
    ):
        source_batches = self._execute(op.source, context)
        return _SchemaAndBatches.from_dataframe(
            _as_df(self._execute(op.source, context)).limit(op.num_rows),
            source_batches.metrics,
        )

    def _execute_order_by(
        self, op: op_graph.op.OrderBy, context: _InMemoryExecutionContext
    ):
        source_batches = self._execute(op.source, context)
        return _SchemaAndBatches.from_dataframe(
            _as_df(source_batches).sort(op.columns, descending=op.desc),
            source_batches.metrics,
        )

    def _row_filter_to_condition(  # noqa:  PLR0911, C901
        self, row_filter: op_graph.RowFilter
    ) -> pl.Expr:
        match row_filter:
            case op_graph.row_filter.CompareColumnToLiteral():
                match row_filter.comparison_type:
                    case table_pb2.COMPARISON_TYPE_EQ:
                        return pl.col(row_filter.column_name) == row_filter.literal
                    case table_pb2.COMPARISON_TYPE_NE:
                        return pl.col(row_filter.column_name) != row_filter.literal
                    case table_pb2.COMPARISON_TYPE_LT:
                        return pl.col(row_filter.column_name) < row_filter.literal
                    case table_pb2.COMPARISON_TYPE_GT:
                        return pl.col(row_filter.column_name) > row_filter.literal
                    case table_pb2.COMPARISON_TYPE_LE:
                        return pl.col(row_filter.column_name) <= row_filter.literal
                    case table_pb2.COMPARISON_TYPE_GE:
                        return pl.col(row_filter.column_name) >= row_filter.literal
                    case _:
                        raise op_graph.OpParseError(
                            "unknown comparison type value in row filter",
                            value=row_filter.comparison_type,
                        )
            case op_graph.row_filter.CombineFilters():
                sub_filters = (
                    self._row_filter_to_condition(sub_filter)
                    for sub_filter in row_filter.row_filters
                )
                match row_filter.combination_op:
                    case table_pb2.LOGICAL_COMBINATION_ANY:
                        return functools.reduce(
                            lambda left, right: left | right, sub_filters
                        )
                    case table_pb2.LOGICAL_COMBINATION_ALL:
                        return functools.reduce(
                            lambda left, right: left & right, sub_filters
                        )
                    case _:
                        raise op_graph.OpParseError(
                            "unknown logical combination op value in row filter",
                            value=row_filter.combination_op,
                        )

    def _execute_filter_rows(
        self, op: op_graph.op.FilterRows, context: _InMemoryExecutionContext
    ) -> _SchemaAndBatches:
        source_batches = self._execute(op.source, context)
        return _SchemaAndBatches.from_dataframe(
            _as_df(source_batches).filter(self._row_filter_to_condition(op.row_filter)),
            source_batches.metrics,
        )

    def _execute_embedding_metrics(
        self, op: op_graph.op.EmbeddingMetrics, context: _InMemoryExecutionContext
    ) -> _SchemaAndBatches:
        source_batches = self._execute(op.table, context)
        embedding_df = _as_df(source_batches)
        if len(embedding_df) < _MIN_EMBEDDINGS_FOR_EMBEDDINGS_SUMMARY:
            # downstream consumers handle empty metadata by substituting their
            # own values
            return source_batches

        # before it was configurable, this op assumed that the column's name was
        # this hardcoded name
        embedding_column_name = op.embedding_column_name or "embedding"
        embedding = embedding_df[embedding_column_name].to_numpy()

        metrics = source_batches.metrics.copy()
        metrics["ne_sum"] = embedding_metric.ne_sum(embedding, normalize=True)
        metrics["condition_number"] = embedding_metric.condition_number(
            embedding, normalize=True
        )
        metrics["rcondition_number"] = embedding_metric.rcondition_number(
            embedding, normalize=True
        )
        metrics["stable_rank"] = embedding_metric.stable_rank(embedding, normalize=True)
        return _SchemaAndBatches.from_dataframe(embedding_df, metrics=metrics)

    def _execute_embedding_coordinates(
        self, op: op_graph.op.EmbeddingCoordinates, context: _InMemoryExecutionContext
    ) -> _SchemaAndBatches:
        source_batches = self._execute(op.table, context)
        embedding_df = _as_df(source_batches)

        # before it was configurable, this op assumed that the column's name was
        # this hardcoded name
        embedding_column_name = op.embedding_column_name or "embedding"

        # the neighbors of a point includes itself. That does mean, that an n_neighbors
        # value of less than 3 simply does not work
        if len(embedding_df) < _MIN_EMBEDDINGS_FOR_EMBEDDINGS_SUMMARY:
            coordinates_df = embedding_df.with_columns(
                pl.Series(
                    name=embedding_column_name,
                    values=[[0.0] * op.n_components] * len(embedding_df),
                    dtype=pl.Array(pl.Float32, op.n_components),
                )
            )
            return _SchemaAndBatches.from_dataframe(
                coordinates_df, source_batches.metrics
            )

        embedding = embedding_df[embedding_column_name].to_numpy()

        n_neighbors = 15
        init = "spectral"
        # y spectral initialisation cannot be used when n_neighbors
        # is greater or equal to the number of samples
        if embedding.shape[0] <= n_neighbors:
            init = "random"
            # n_neighbors is larger than the dataset size; truncating to X.shape[0] - 1
            n_neighbors = embedding.shape[0] - 1

        # import umap locally to reduce loading time
        # TODO(Hunterlige): Replace with lazy_import
        from umap import umap_ as umap

        projector = umap.UMAP(
            n_neighbors=n_neighbors,
            n_components=op.n_components,
            metric=op.metric,
            init=init,
            low_memory=False,
            verbose=True,
        )

        _logger.info(
            "generating embedding coordinates",
            num_embeddings=embedding_df.shape[0],
            metric=op.metric,
            n_neighbors=n_neighbors,
            init=init,
            n_components=op.n_components,
        )
        coordinates = projector.fit_transform(embedding)
        coordinates_df = embedding_df.with_columns(
            pl.Series(
                name=embedding_column_name,
                values=coordinates,
                dtype=pl.Array(pl.Float32, coordinates.shape[1]),
            )
        )
        return _SchemaAndBatches.from_dataframe(coordinates_df, source_batches.metrics)

    def _execute_distinct_rows(
        self, op: op_graph.op.DistinctRows, context: _InMemoryExecutionContext
    ) -> _SchemaAndBatches:
        source_batches = self._execute(op.source, context)
        return _SchemaAndBatches.from_dataframe(
            _as_df(source_batches).unique(), source_batches.metrics
        )

    def _execute_join(
        self, op: op_graph.op.Join, context: _InMemoryExecutionContext
    ) -> _SchemaAndBatches:
        left_batches = self._execute(op.left_source, context)
        right_batches = self._execute(op.right_source, context)
        left_df = _as_df(left_batches)
        right_df = _as_df(right_batches)

        match op.how:
            case table_pb2.JOIN_TYPE_INNER:
                join_type = "inner"
            case table_pb2.JOIN_TYPE_LEFT_OUTER:
                join_type = "left"
            case _:
                join_type = "inner"

        # in our join semantics we drop columns from the right source on conflict
        right_df = right_df.select(
            [
                col
                for col in right_df.columns
                if col in op.right_join_columns or col not in left_df.columns
            ]
        )
        metrics = right_batches.metrics.copy()
        metrics.update(left_batches.metrics)

        # polars doesn't behave so well when one side is empty, just
        # compute the trivial empty join when the result is guaranteed
        # to be empty instead.
        if len(left_df) == 0 or len(right_df) == 0 and join_type == "inner":
            return _SchemaAndBatches(
                schema=op.schema.to_arrow(),
                batches=op.schema.to_arrow().empty_table().to_batches(),
                metrics=metrics,
            )

        return _SchemaAndBatches.from_dataframe(
            left_df.join(
                right_df,
                left_on=op.left_join_columns,
                right_on=op.right_join_columns,
                how=join_type,
            ),
            metrics,
        )

    def _execute_empty(self, op: op_graph.op.Empty, context: _InMemoryExecutionContext):
        empty_table = pa.schema([]).empty_table()
        return _SchemaAndBatches(
            empty_table.schema, empty_table.to_batches(), metrics={}
        )

    def _execute_concat(
        self, op: op_graph.op.Concat, context: _InMemoryExecutionContext
    ):
        source_batches = [self._execute(table, context) for table in op.tables]
        dataframes = [_as_df(batches) for batches in source_batches]
        metrics = dict[str, Any]()
        for batches in source_batches:
            metrics.update(batches.metrics)
        return _SchemaAndBatches.from_dataframe(pl.concat(dataframes), metrics=metrics)

    def _execute_unnest_struct(
        self, op: op_graph.op.UnnestStruct, context: _InMemoryExecutionContext
    ):
        source_batches = self._execute(op.source, context)
        return _SchemaAndBatches.from_dataframe(
            _as_df(source_batches).unnest(op.struct_column_name), source_batches.metrics
        )

    def _execute_nest_into_struct(
        self, op: op_graph.op.NestIntoStruct, context: _InMemoryExecutionContext
    ):
        source_batches = self._execute(op.source, context)
        non_struct_columns = [
            name
            for name in source_batches.schema.names
            if name not in op.column_names_to_nest
        ]
        return _SchemaAndBatches.from_dataframe(
            _as_df(source_batches).select(
                *non_struct_columns,
                pl.struct(op.column_names_to_nest).alias(op.struct_column_name),
            ),
            source_batches.metrics,
        )

    def _execute_add_literal_column(
        self, op: op_graph.op.AddLiteralColumn, context: _InMemoryExecutionContext
    ):
        pl_schema = cast(
            pl.DataFrame, pl.from_arrow(op.column_arrow_schema.empty_table())
        ).schema
        name, dtype = next(iter(pl_schema.items()))

        source_batches = self._execute(op.source, context)
        return _SchemaAndBatches.from_dataframe(
            _as_df(source_batches).with_columns(pl.lit(op.literal, dtype).alias(name)),
            source_batches.metrics,
        )

    def _execute_combine_columns(
        self, op: op_graph.op.CombineColumns, context: _InMemoryExecutionContext
    ):
        source_batches = self._execute(op.source, context)
        source_df = _as_df(source_batches)
        match op.reduction:
            case op_graph.ConcatString():
                # if we do not ignore nulls then all concatenated rows that
                # have a single column that contain a null value will be output
                # as null.
                result_df = source_df.with_columns(
                    pl.concat_str(
                        [pl.col(col) for col in op.column_names],
                        separator=op.reduction.separator,
                        ignore_nulls=True,
                    ).alias(op.combined_column_name)
                )

        return _SchemaAndBatches.from_dataframe(result_df, source_batches.metrics)

    def _execute_embed_column(
        self, op: op_graph.op.EmbedColumn, context: _InMemoryExecutionContext
    ):
        source_batches = self._execute(op.source, context)
        source_df = _as_df(source_batches)
        to_embed = source_df[op.column_name].cast(pl.String())

        embed_context = EmbedTextContext(
            inputs=to_embed,
            model_name=op.model_name,
            tokenizer_name=op.tokenizer_name,
            expected_vector_length=op.expected_vector_length,
            expected_coordinate_bitwidth=op.expected_coordinate_bitwidth,
        )
        result = self._text_embedder.embed(embed_context)

        result_df = source_df.with_columns(
            result.embeddings.alias(op.embedding_column_name)
        ).drop_nulls(op.embedding_column_name)

        return _SchemaAndBatches.from_dataframe(
            result_df,
            source_batches.metrics,
        )

    def _execute_embed_node2vec_from_edge_lists(
        self,
        op: op_graph.op.EmbedNode2vecFromEdgeLists,
        context: _InMemoryExecutionContext,
    ):
        dtypes: set[pa.DataType] = set()
        entities_dtypes: dict[str, pa.DataType] = {}
        for edge_list in op.edge_list_tables:
            schema = edge_list.table.schema.to_arrow()
            start_dtype = schema.field(edge_list.start_column_name).type
            end_dtype = schema.field(edge_list.end_column_name).type
            dtypes.add(start_dtype)
            dtypes.add(end_dtype)
            entities_dtypes[edge_list.start_column_name] = start_dtype
            entities_dtypes[edge_list.end_column_name] = end_dtype

        start_fields = [pa.field(f"start_id_{dtype}", dtype) for dtype in dtypes]
        start_fields.append(pa.field("start_source", pa.large_string()))
        start_id_column_names = [field.name for field in start_fields]

        end_fields = [pa.field(f"end_id_{dtype}", dtype) for dtype in dtypes]
        end_fields.append(pa.field("end_source", pa.large_string()))
        end_id_column_names = [field.name for field in end_fields]

        fields = start_fields + end_fields
        empty_edges_table = pl.from_arrow(pa.schema(fields).empty_table())

        if isinstance(empty_edges_table, pl.Series):
            empty_edges_table = empty_edges_table.to_frame()

        metrics = dict[str, Any]()

        def edge_generator():
            for edge_list in op.edge_list_tables:
                start_column_name = edge_list.start_column_name
                end_column_name = edge_list.end_column_name
                start_column_type_name = entities_dtypes[start_column_name]
                end_column_type_name = entities_dtypes[end_column_name]
                source_batches = self._execute(edge_list.table, context)
                metrics.update(source_batches.metrics)
                for batch in source_batches.batches:
                    yield (
                        _as_df(batch)
                        .with_columns(
                            pl.col(edge_list.start_column_name).alias(
                                f"start_id_{start_column_type_name}"
                            ),
                            pl.lit(edge_list.start_entity_name).alias("start_source"),
                            pl.col(edge_list.end_column_name).alias(
                                f"end_id_{end_column_type_name}"
                            ),
                            pl.lit(edge_list.end_entity_name).alias("end_source"),
                        )
                        .select(
                            f"start_id_{start_column_type_name}",
                            "start_source",
                            f"end_id_{end_column_type_name}",
                            "end_source",
                        )
                    )

        edges = pl.concat(
            [
                empty_edges_table,
                *(edge_list for edge_list in edge_generator()),
            ],
            rechunk=False,
            how="diagonal",
        )

        n2v_space = embed.Space(
            edges=edges,
            start_id_column_names=start_id_column_names,
            end_id_column_names=end_id_column_names,
            directed=True,
        )
        n2v_runner = embed.Node2Vec(
            space=n2v_space,
            dim=op.ndim,
            walk_length=op.walk_length,
            window=op.window,
            p=op.p,
            q=op.q,
            alpha=op.alpha,
            min_alpha=op.min_alpha,
            negative=op.negative,
        )
        n2v_runner.train(epochs=op.epochs)
        return _SchemaAndBatches.from_dataframe(n2v_runner.wv.to_polars(), metrics)

    def _do_execute(  # noqa: PLR0911, PLR0912, C901
        self,
        op: op_graph.Op,
        context: _InMemoryExecutionContext,
    ) -> _SchemaAndBatches:
        if self._is_sql_compatible(op) and self._staging_db:
            query = sql.parse_op_graph(
                op,
                self._staging_db.query_for_blobs,
                self._staging_db.query_for_vector_search,
            )
            expected_schema = op.schema
            return _patch_batch_reader_schema(
                self._staging_db.run_select_query(query, context.current_slice_args),
                new_schema=expected_schema.to_arrow(),
                metrics={},
            )

        match op:
            case op_graph.op.SelectFromStaging():
                raise InternalError("SelectFromStaging should always be lowered to sql")
            case op_graph.op.SelectFromVectorStaging():
                raise InternalError(
                    "SelectFromVectorStaging should always be lowered to sql"
                )
            case op_graph.op.ReadFromParquet():
                return self._execute_read_from_parquet(op, context)
            case op_graph.op.RenameColumns():
                return self._execute_rename_columns(op, context)
            case op_graph.op.Join():
                return self._execute_join(op, context)
            case op_graph.op.SelectColumns():
                return self._execute_select_columns(op, context)
            case op_graph.op.LimitRows():
                return self._execute_limit_rows(op, context)
            case op_graph.op.OrderBy():
                return self._execute_order_by(op, context)
            case op_graph.op.FilterRows():
                return self._execute_filter_rows(op, context)
            case op_graph.op.DistinctRows():
                return self._execute_distinct_rows(op, context)
            case (
                op_graph.op.SetMetadata()
                | op_graph.op.UpdateMetadata()
                | op_graph.op.RemoveFromMetadata()
                | op_graph.op.UpdateFeatureTypes()
            ):
                return self._execute(op.source, context)
            case op_graph.op.EmbeddingMetrics() as op:
                return self._execute_embedding_metrics(op, context)
            case op_graph.op.EmbeddingCoordinates():
                return self._execute_embedding_coordinates(op, context)
            case op_graph.op.RollupByAggregation() as op:
                return self._execute_rollup_by_aggregation(op, context)
            case op_graph.op.Empty():
                return self._execute_empty(op, context)
            case op_graph.op.EmbedNode2vecFromEdgeLists():
                return self._execute_embed_node2vec_from_edge_lists(op, context)
            case op_graph.op.Concat():
                return self._execute_concat(op, context)
            case op_graph.op.UnnestStruct():
                return self._execute_unnest_struct(op, context)
            case op_graph.op.NestIntoStruct():
                return self._execute_nest_into_struct(op, context)
            case op_graph.op.AddLiteralColumn():
                return self._execute_add_literal_column(op, context)
            case op_graph.op.CombineColumns():
                return self._execute_combine_columns(op, context)
            case op_graph.op.EmbedColumn():
                return self._execute_embed_column(op, context)

    def _execute(
        self,
        op: op_graph.Op,
        context: _InMemoryExecutionContext,
    ) -> _SchemaAndBatches:
        with structlog.contextvars.bound_contextvars(
            executing_op=op.expected_oneof_field()
        ):
            sliced_table = _SlicedTable(op, context.current_slice_args)
            if sliced_table in context.computed_batches_for_op_graph:
                _logger.info("using previously computed table for op")
                return context.computed_batches_for_op_graph[sliced_table]

            try:
                _logger.info("starting op execution")
                batches = self._do_execute(op=op, context=context)
            finally:
                _logger.info("op execution complete")

            if (
                sliced_table in context.output_tables
                or sliced_table in context.reused_tables
            ):
                context.computed_batches_for_op_graph[sliced_table] = batches
            return batches

    def execute(
        self, context: ExecutionContext
    ) -> Ok[ExecutionResult] | BadArgumentError:
        in_memory_context = _InMemoryExecutionContext(context)

        for table_context in context.tables_to_compute:
            in_memory_context.current_output_context = table_context
            sliced_table = _SlicedTable(
                table_context.table_op_graph, table_context.sql_output_slice_args
            )
            if sliced_table not in in_memory_context.computed_batches_for_op_graph:
                self._execute(sliced_table.op_graph, in_memory_context)

        return Ok(
            InMemoryExecutionResult.make(
                self._storage_manager, in_memory_context, context
            )
        )
