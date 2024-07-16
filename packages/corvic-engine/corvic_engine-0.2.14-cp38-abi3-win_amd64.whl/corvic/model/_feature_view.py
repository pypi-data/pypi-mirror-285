"""Feature views."""

from __future__ import annotations

import dataclasses
import functools
import uuid
from collections.abc import Iterable
from typing import Any, Final, TypeAlias

from more_itertools import flatten

from corvic import orm, system
from corvic.model._defaults import get_default_client
from corvic.model._source import Source, SourceID
from corvic.model._wrapped_orm import WrappedOrmObject
from corvic.result import BadArgumentError
from corvic.table import (
    DataclassAsTypedMetadataMixin,
    RowFilter,
    Schema,
    Table,
    feature_type,
    row_filter,
)

FeatureViewID: TypeAlias = orm.FeatureViewID
FeatureViewSourceID: TypeAlias = orm.FeatureViewSourceID


class Column:
    """A logical representation of a column to use in filter predicates.

    Columns are identified by name.
    """

    _column_name: Final[str]

    def __init__(self, column_name: str):
        """Creates a new instance of Column.

        Args:
            column_name: Name of the column
        """
        self._column_name = column_name

    def eq(self, value: Any) -> RowFilter:
        """Return rows where column is equal to a value."""
        return row_filter.eq(column_name=self._column_name, literal=value)

    def ne(self, value: Any) -> RowFilter:
        """Return rows where column is not equal to a value."""
        return row_filter.ne(column_name=self._column_name, literal=value)

    def gt(self, value: Any) -> RowFilter:
        """Return rows where column is greater than a value."""
        return row_filter.gt(column_name=self._column_name, literal=value)

    def lt(self, value: Any) -> RowFilter:
        """Return rows where column is less than a value."""
        return row_filter.lt(column_name=self._column_name, literal=value)

    def ge(self, value: Any) -> RowFilter:
        """Return rows where column is greater than or equal to a value."""
        return row_filter.ge(column_name=self._column_name, literal=value)

    def le(self, value: Any) -> RowFilter:
        """Return rows where column is less than or equal to a value."""
        return row_filter.le(column_name=self._column_name, literal=value)

    def in_(self, value: list[Any]) -> RowFilter:
        """Return rows where column matches any in a list of values."""
        return row_filter.in_(column_name=self._column_name, literals=value)


@dataclasses.dataclass(frozen=True)
class FkeyRelationship:
    """A foreign key relationship between sources."""

    source_with_fkey: SourceID
    fkey_column_name: str
    referenced_source: SourceID
    pkey_column_name: str


@dataclasses.dataclass(frozen=True)
class Relationship:
    """A connection between two sources within a FeatureView."""

    from_feature_view_source: FeatureViewSource
    to_feature_view_source: FeatureViewSource

    fkey_relationship: FkeyRelationship

    @property
    def from_source(self) -> Source:
        return self.from_feature_view_source.source

    @property
    def to_source(self) -> Source:
        return self.to_feature_view_source.source

    @property
    def from_column_name(self) -> str:
        if self.from_source.id == self.fkey_relationship.source_with_fkey:
            return self.fkey_relationship.fkey_column_name
        return self.fkey_relationship.pkey_column_name

    @property
    def to_column_name(self) -> str:
        if self.to_source.id == self.fkey_relationship.source_with_fkey:
            return self.fkey_relationship.fkey_column_name
        return self.fkey_relationship.pkey_column_name

    @property
    def new_column_name(self) -> str:
        return self.fkey_relationship.fkey_column_name

    def joined_table(self) -> Table:
        start_table = self.from_feature_view_source.table.rename_columns(
            {self.from_column_name: self.new_column_name}
        )
        end_table = self.to_feature_view_source.table.rename_columns(
            {self.to_column_name: self.new_column_name}
        )

        return start_table.join(
            end_table,
            left_on=self.new_column_name,
            right_on=self.new_column_name,
            how="inner",
        )

    def edge_list(self) -> Iterable[tuple[Any, Any]]:
        start_pk = self.from_feature_view_source.table.schema.get_primary_key()
        end_pk = self.to_feature_view_source.table.schema.get_primary_key()

        if not start_pk or not end_pk:
            raise BadArgumentError(
                "both sources must have a primary key to render edge list"
            )

        if self.from_column_name == start_pk.name:
            result_columns = (self.new_column_name, end_pk.name)
        else:
            result_columns = (start_pk.name, self.new_column_name)

        result = self.joined_table().select(result_columns)

        for batch in result.to_polars().unwrap_or_raise():
            for row in batch.rows(named=True):
                yield (row[result_columns[0]], row[result_columns[1]])


@dataclasses.dataclass(frozen=True)
class FeatureViewSource(WrappedOrmObject[FeatureViewSourceID, orm.FeatureViewSource]):
    """A table from a source with some extra operations defined by a feature view."""

    source: Source

    def _sub_orm_objects(self, orm_object: orm.FeatureViewSource) -> Iterable[orm.Base]:
        _ = (orm_object,)
        return []

    @functools.cached_property
    def table(self):
        return Table.from_bytes(self.client, self.orm_self.table_op_graph)


@dataclasses.dataclass(kw_only=True)
class FeatureViewEdgeTableMetadata(DataclassAsTypedMetadataMixin):
    """Metadata attached to edge tables; notes important columns and provenance."""

    @classmethod
    def metadata_key(cls):
        return "space-edge_table-metadata"

    start_source_name: str
    end_source_name: str
    start_source_column_name: str
    end_source_column_name: str


@dataclasses.dataclass(kw_only=True)
class FeatureViewRelationshipsMetadata(DataclassAsTypedMetadataMixin):
    """Metadata attached to relationship path for feature view edge tables."""

    @classmethod
    def metadata_key(cls):
        return "space-relationships-metadata"

    relationship_path: list[str]


@dataclasses.dataclass(kw_only=True)
class FeatureViewSourceColumnRenames(DataclassAsTypedMetadataMixin):
    """Metadata attached to feature space source tables to remember renamed columns."""

    @classmethod
    def metadata_key(cls):
        return "space_source-column_renames-metadata"

    column_renames: dict[str, str]


@dataclasses.dataclass(frozen=True)
class FeatureView(WrappedOrmObject[FeatureViewID, orm.FeatureView]):
    """FeatureViews describe how Sources should be modeled to create a feature space.

    Example:
    >>> FeatureView.create()
    >>>    .with_source(
    >>>        customer_source.id,
    >>>        row_filter=Column("customer_name").eq("Denis").or_(Column("id").lt(3)),
    >>>        drop_disconnected=True,
    >>>    )
    >>>    .with_source(
    >>>        order_source,
    >>>        include_columns=["id", "ordered_item"],
    >>>    )
    >>>    .wth_relationship(customer_source.id, order_source.id, directional=False)
    """

    source_id_to_feature_view_source: dict[SourceID, FeatureViewSource]
    output_sources: set[SourceID]
    relationships: list[Relationship]

    def _sub_orm_objects(self, orm_object: orm.FeatureView) -> Iterable[orm.Base]:
        _ = (orm_object,)
        return []

    @functools.cached_property
    def sources(self) -> list[Source]:
        return [
            feature_view_source.source
            for feature_view_source in self.source_id_to_feature_view_source.values()
        ]

    def _calculate_paths_to_outputs(self, output: SourceID, rels: list[Relationship]):
        paths: list[list[Relationship]] = []
        for rel in rels:
            if rel.from_source.id == output:
                if rel.to_source.id in self.output_sources:
                    paths.append([rel])
                else:
                    child_paths = self._calculate_paths_to_outputs(
                        rel.to_source.id,
                        [  # we only want to use a fkey relationship once per path
                            next_rel
                            for next_rel in rels
                            if next_rel.fkey_relationship != rel.fkey_relationship
                        ],
                    )
                    paths.extend([rel, *child_path] for child_path in child_paths)
        return paths

    @staticmethod
    def _find_start_end_columns(rels: list[Relationship]) -> tuple[str, str]:
        if not rels:
            raise BadArgumentError("must provide at least one relationship")

        if rels[0].fkey_relationship.source_with_fkey == rels[0].from_source.id:
            start_field = rels[
                0
            ].from_feature_view_source.table.schema.get_primary_key()
            if not start_field:
                raise BadArgumentError(
                    "configuration requires column to have a primary key",
                    source_name=rels[0].from_feature_view_source.source.name,
                )
            start_col = start_field.name
        else:
            start_col = rels[0].new_column_name

        if rels[-1].fkey_relationship.source_with_fkey == rels[-1].to_source.id:
            end_field = rels[-1].to_feature_view_source.table.schema.get_primary_key()
            if not end_field:
                raise BadArgumentError(
                    "configuration requires source to have primary key",
                    source_name=rels[-1].to_feature_view_source.source.name,
                )
            end_col = end_field.name
        else:
            end_col = rels[-1].new_column_name

        return start_col, end_col

    def output_edge_tables(self) -> list[Table]:
        paths_between_outputs = list(
            flatten(
                self._calculate_paths_to_outputs(output, self.relationships)
                for output in self.output_sources
            )
        )

        def update_renames(new_rel: Relationship, column_renames: dict[str, str]):
            column_renames[new_rel.from_column_name] = new_rel.new_column_name
            column_renames[new_rel.to_column_name] = new_rel.new_column_name

        def find_latest_name(name: str, column_renames: dict[str, str]):
            while name in column_renames:
                new_name = column_renames[name]
                if new_name == name:
                    break
                name = new_name
            return name

        edge_tables = list[Table]()
        for path in paths_between_outputs:
            path_itr = iter(path)
            rel = next(path_itr)
            table = rel.joined_table()
            column_renames = dict[str, str]()

            update_renames(rel, column_renames)
            for rel in path_itr:
                table = table.rename_columns(
                    {
                        find_latest_name(
                            rel.from_column_name, column_renames
                        ): rel.new_column_name
                    }
                )
                table = table.join(
                    rel.to_feature_view_source.table.rename_columns(
                        {rel.to_column_name: rel.new_column_name}
                    ),
                    left_on=rel.new_column_name,
                    right_on=rel.new_column_name,
                    suffix=f"_{rel.to_feature_view_source.source.name}",
                )
                update_renames(rel, column_renames)
            start_col, end_col = self._find_start_end_columns(path)
            relationship_path = [
                path[0].from_source.name,
                *(p.to_source.name for p in path),
            ]

            table = table.update_typed_metadata(
                FeatureViewEdgeTableMetadata(
                    start_source_name=path[0].from_feature_view_source.source.name,
                    end_source_name=path[-1].to_feature_view_source.source.name,
                    start_source_column_name=find_latest_name(
                        start_col, column_renames
                    ),
                    end_source_column_name=find_latest_name(end_col, column_renames),
                ),
                FeatureViewRelationshipsMetadata(
                    relationship_path=list(relationship_path)
                ),
            )
            edge_tables.append(table)
        return edge_tables

    @classmethod
    def create(cls, client: system.Client | None = None) -> FeatureView:
        """Create a FeatureView."""
        orm_feature_view = orm.FeatureView()
        client = client or get_default_client()
        return FeatureView(
            client,
            orm_feature_view,
            FeatureViewID(),
            source_id_to_feature_view_source={},
            relationships=[],
            output_sources=set(),
        )

    @property
    def feature_view_sources(self) -> list[FeatureViewSource]:
        return list(self.source_id_to_feature_view_source.values())

    @staticmethod
    def _unique_name_for_key_column(source: Source) -> str:
        return f"{source.name}_id-{uuid.uuid4()}"

    def _sanitize_keys(self, new_schema: Schema, source: Source):
        renames = dict[str, str]()
        for field in new_schema:
            match field.ftype:
                case feature_type.PrimaryKey():
                    renames[field.name] = self._unique_name_for_key_column(source)
                case feature_type.ForeignKey(refd_source_id):
                    refd_source = Source.from_id(
                        refd_source_id, self.client
                    ).unwrap_or_raise()
                    renames[field.name] = self._unique_name_for_key_column(refd_source)
                case _:
                    pass
        return renames

    def with_source(
        self,
        source_id: SourceID,
        *,
        row_filter: RowFilter | None = None,
        drop_disconnected: bool = False,
        include_columns: list[str] | None = None,
        output: bool = False,
    ) -> FeatureView:
        """Add a source to to this FeatureView.

        Args:
            source_id: The id of the source to be added
            row_filter: Row level filters to be applied on source
            drop_disconnected: Filter orphan nodes in source
            include_columns: Column level filters to be applied on source
            output: Set to True if this should should be an entity in the ourput

        Example:
        >>> with_source(
        >>>     customer_source_id,
        >>>     row_filter=Column("customer_name").eq("Denis"),
        >>>     drop_disconnected=True,
        >>>     include_columns=["id", "customer_name"],
        >>> )
        """
        # TODO(thunt): Reminder that these new table ops should start
        # from loading the source
        source = Source.from_id(source_id, self.client).unwrap_or_raise()
        new_table = source.table
        if row_filter:
            new_table = new_table.filter_rows(row_filter)
        if include_columns:
            new_table = new_table.select(include_columns)

        renames = self._sanitize_keys(new_table.schema, source)

        if renames:
            new_table = new_table.rename_columns(renames).update_typed_metadata(
                FeatureViewSourceColumnRenames(column_renames=renames)
            )

        orm_feature_view_source = orm.FeatureViewSource(
            table_op_graph=new_table.op_graph.to_bytes(),
            drop_disconnected=drop_disconnected,
        )

        source_id_to_feature_view_source = self.source_id_to_feature_view_source.copy()
        source_id_to_feature_view_source.update(
            {
                source.id: FeatureViewSource(
                    self.client, orm_feature_view_source, FeatureViewSourceID(), source
                )
            }
        )

        output_sources = self.output_sources
        if output:
            primary_key = source.table.schema.get_primary_key()
            if not primary_key:
                raise BadArgumentError(
                    "source must have a primary key to part of the output"
                )
            output_sources = output_sources.union({source.id})

        return dataclasses.replace(
            self,
            orm_self=dataclasses.replace(self.orm_self, id=None),
            source_id_to_feature_view_source=source_id_to_feature_view_source,
            output_sources=output_sources,
        )

    def _check_or_infer_foreign_keys(  # noqa: C901
        self,
        from_source_id: SourceID,
        to_source_id: SourceID,
        from_foreign_key: str | None,
        to_foreign_key: str | None,
    ) -> tuple[str | None, str | None]:
        frm = self.source_id_to_feature_view_source[from_source_id]
        to = self.source_id_to_feature_view_source[to_source_id]

        if from_foreign_key:
            frm_renames = (
                frm.table.get_typed_metadata(
                    FeatureViewSourceColumnRenames
                ).column_renames
                if frm.table.has_typed_metadata(FeatureViewSourceColumnRenames)
                else dict[str, str]()
            )
            foreign_key = frm_renames.get(from_foreign_key, from_foreign_key)
            match frm.table.schema[foreign_key].ftype:
                case feature_type.ForeignKey(referenced_source_id):
                    if referenced_source_id != to.source.id:
                        raise BadArgumentError(
                            "from_foreign_key does not reference to_source_id",
                            to_source_id=str(to.source.id),
                            referenced_source_id=str(referenced_source_id),
                        )
                case _:
                    raise BadArgumentError(
                        "the provided from_foreign_key is not a ForeignKey feature"
                    )
            from_foreign_key = foreign_key

        if to_foreign_key:
            to_renames = (
                to.table.get_typed_metadata(
                    FeatureViewSourceColumnRenames
                ).column_renames
                if to.table.has_typed_metadata(FeatureViewSourceColumnRenames)
                else dict[str, str]()
            )
            foreign_key = to_renames.get(to_foreign_key, to_foreign_key)
            match to.table.schema[foreign_key].ftype:
                case feature_type.ForeignKey(referenced_source_id):
                    if referenced_source_id != frm.source.id:
                        raise BadArgumentError(
                            "to_foreign_key does not reference from_source_id",
                            from_source_id=str(frm.source.id),
                            referenced_source_id=str(referenced_source_id),
                        )
                case _:
                    raise BadArgumentError(
                        "the provided to_foreign_key is not a ForeignKey feature"
                    )
            to_foreign_key = foreign_key

        if not from_foreign_key and not to_foreign_key:
            from_foreign_keys = [
                field.name for field in frm.table.schema.get_foreign_keys(to.source.id)
            ]
            to_foreign_keys = [
                field.name for field in to.table.schema.get_foreign_keys(frm.source.id)
            ]

            if (
                (from_foreign_keys and to_foreign_keys)
                or len(from_foreign_keys) > 1
                or len(to_foreign_keys) > 1
            ):
                raise BadArgumentError(
                    "relationship is ambiguous:"
                    + "provide from_foreign_key or to_foreign_key to disambiguate",
                    from_foreign_keys=from_foreign_keys,
                    to_foreign_keys=to_foreign_keys,
                )
            if from_foreign_keys:
                from_foreign_key = from_foreign_keys[0]
            if to_foreign_keys:
                to_foreign_key = to_foreign_keys[0]

        return (from_foreign_key, to_foreign_key)

    def with_all_implied_relationships(self) -> FeatureView:
        """Automatically define non-directional relationships based on foreign keys."""
        new_feature_view = self
        for feature_view_source in self.feature_view_sources:
            for field in feature_view_source.source.table.schema:
                match field.ftype:
                    case feature_type.ForeignKey(referenced_source_id):
                        if (
                            referenced_source_id
                            in self.source_id_to_feature_view_source
                        ):
                            # We don't know the intended direction, add both directions
                            new_feature_view = new_feature_view.with_relationship(
                                referenced_source_id,
                                feature_view_source.source.id,
                                to_foreign_key=field.name,
                                directional=False,
                            )
                    case _:
                        pass
        return new_feature_view

    def with_relationship(
        self,
        from_source_id: SourceID,
        to_source_id: SourceID,
        *,
        from_foreign_key: str | None = None,
        to_foreign_key: str | None = None,
        directional: bool = False,
    ) -> FeatureView:
        """Define relationship between two sources.

        Args:
            from_source_id: The ID of the source on the "from" side (if dircectional)
            to_source_id: The ID of the source on the "to" side (if dircectional)
            from_foreign_key: The foreign key to use to match on the "from"
                source. Required if there is more than one foreign key relationship
                linking the sources. Cannot be used with "to_foreign_key".
            to_foreign_key: The foreign key to use to match on the "to"
                source. Required if there is more than one foreign key relationship
                linking the sources. Cannot be used with "from_foreign_key"
            directional: Whether to load graph as directional

        Example:
        >>> with_relationship(customer_source.id, order_source.id, directional=False)
        """
        from_feature_view_source = self.source_id_to_feature_view_source.get(
            from_source_id
        )
        if not from_feature_view_source:
            raise BadArgumentError(
                "from_source_id does not match any source in this feature view",
                from_source_id=str(from_source_id),
            )
        to_feature_view_source = self.source_id_to_feature_view_source.get(to_source_id)
        if not to_feature_view_source:
            raise BadArgumentError(
                "to_source_id does not match any source in this feature view",
                to_source_id=str(to_source_id),
            )

        if from_foreign_key and to_foreign_key:
            raise BadArgumentError(
                "only one of from_foreign_key and to_foreign_key may be provided",
                to_source_id=str(to_source_id),
            )

        from_foreign_key, to_foreign_key = self._check_or_infer_foreign_keys(
            from_source_id, to_source_id, from_foreign_key, to_foreign_key
        )

        if from_foreign_key:
            pk = self.source_id_to_feature_view_source[
                to_source_id
            ].table.schema.get_primary_key()
            if not pk:
                raise BadArgumentError(
                    "source has no primary key, "
                    + "so it cannot be referenced by foreign key",
                    from_source_id=str(from_source_id),
                )

            fkey_relationship = FkeyRelationship(
                source_with_fkey=from_source_id,
                fkey_column_name=from_foreign_key,
                referenced_source=to_source_id,
                pkey_column_name=pk.name,
            )
        elif to_foreign_key:
            pk = self.source_id_to_feature_view_source[
                from_source_id
            ].table.schema.get_primary_key()
            if not pk:
                raise BadArgumentError(
                    "source has no primary key, "
                    + "so it cannot be referenced by foreign key",
                    to_source_id=str(to_source_id),
                )
            fkey_relationship = FkeyRelationship(
                source_with_fkey=to_source_id,
                fkey_column_name=to_foreign_key,
                referenced_source=from_source_id,
                pkey_column_name=pk.name,
            )
        else:
            raise BadArgumentError(
                "foreign key relationship was not provided and could not be inferred"
            )

        relationships = [dataclasses.replace(val) for val in self.relationships]

        relationships.append(
            Relationship(
                from_feature_view_source=from_feature_view_source,
                to_feature_view_source=to_feature_view_source,
                fkey_relationship=fkey_relationship,
            )
        )
        if not directional:
            relationships.append(
                Relationship(
                    from_feature_view_source=to_feature_view_source,
                    to_feature_view_source=from_feature_view_source,
                    fkey_relationship=fkey_relationship,
                )
            )

        return dataclasses.replace(
            self,
            orm_self=dataclasses.replace(self.orm_self, id=None),
            relationships=relationships,
        )
