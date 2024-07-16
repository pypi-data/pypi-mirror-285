"""Spaces."""

from __future__ import annotations

import abc
import dataclasses
import uuid
from collections.abc import Iterable, Mapping
from typing import Literal, TypeAlias

import polars as pl
from typing_extensions import Self, deprecated

from corvic import embed, op_graph, orm, system
from corvic.model._feature_view import FeatureView, FeatureViewEdgeTableMetadata
from corvic.model._source import Source, SourceID
from corvic.model._wrapped_orm import WrappedOrmObject
from corvic.result import BadArgumentError, NotFoundError, Ok
from corvic.table import Table
from corvic_generated.algorithm.graph.v1 import graph_pb2

SpaceID: TypeAlias = orm.SpaceID

_DEFAULT_CONCAT_SEPARATOR = " "


@dataclasses.dataclass(frozen=True)
class Space(WrappedOrmObject[SpaceID, orm.Space]):
    """Spaces apply embedding methods to FeatureViews.

    Example:
    >>> space = Space.node2vec(feature_view, dim=10, walk_length=10, window=10)
    """

    feature_view: FeatureView

    @classmethod
    @abc.abstractmethod
    def create(
        cls, feature_view: FeatureView, client: system.Client | None = None
    ) -> Ok[Self] | BadArgumentError: ...

    @classmethod
    @deprecated("build a RelationalSpace instead")
    def node2vec(  # noqa: PLR0913
        cls,
        feature_view: FeatureView,
        *,
        dim: int,
        walk_length: int,
        window: int,
        p: float = 1.0,
        q: float = 1.0,
        batch_words: int | None = None,
        alpha: float = 0.025,
        seed: int | None = None,
        workers: int | None = None,
        min_alpha: float = 0.0001,
        negative: int = 5,
    ) -> embed.Node2Vec:
        """Run Node2Vec on the graph described by the feature view.

        Args:
            feature_view: The feature view to run Node2Vec on
            dim: The dimensionality of the embedding
            walk_length: Length of the random walk to be computed
            window: Size of the window. This is half of the context,
                as the context is all nodes before `window` and
                after `window`.
            p: The higher the value, the lower the probability to return to
                the previous node during a walk.
            q: The higher the value, the lower the probability to return to
                a node connected to a previous node during a walk.
            alpha: Initial learning rate
            min_alpha: Final learning rate
            negative: Number of negative samples
            seed: Random seed
            batch_words: Target size (in nodes) for batches of examples passed
                to worker threads
            workers: Number of threads to use. Default is to select number of threads
                as needed. Setting this to a non-default value incurs additional
                thread pool creation overhead.

        Returns:
            A Space
        """
        if not feature_view.relationships:
            raise BadArgumentError("Node2Vec requires some relationships")

        edge_tables = feature_view.output_edge_tables()
        if not edge_tables:
            raise BadArgumentError(
                "Node2Vec requires some with_sources to be output=True"
            )

        def edge_generator():
            for table in feature_view.output_edge_tables():
                edge_table_info = table.get_typed_metadata(FeatureViewEdgeTableMetadata)
                for batch in table.to_polars().unwrap_or_raise():
                    yield batch.with_columns(
                        pl.col(edge_table_info.start_source_column_name).alias(
                            "start_id"
                        ),
                        pl.lit(edge_table_info.start_source_name).alias("start_source"),
                        pl.col(edge_table_info.end_source_column_name).alias("end_id"),
                        pl.lit(edge_table_info.end_source_name).alias("end_source"),
                    ).select("start_id", "start_source", "end_id", "end_source")

        n2v_space = embed.Space(
            pl.concat((edge_list for edge_list in edge_generator()), rechunk=False),
            start_id_column_names=("start_id", "start_source"),
            end_id_column_names=("end_id", "end_source"),
            directed=True,
        )
        return embed.Node2Vec(
            space=n2v_space,
            dim=dim,
            walk_length=walk_length,
            window=window,
            p=p,
            q=q,
            alpha=alpha,
            min_alpha=min_alpha,
            negative=negative,
            seed=seed,
            batch_words=batch_words,
            workers=workers,
        )


@dataclasses.dataclass(frozen=True)
class Node2VecParameters:
    dim: int = 10
    walk_length: int = 10
    window: int = 10
    p: float = 1.0
    q: float = 1.0
    alpha: float = 0.025
    min_alpha: float = 0.0001
    negative: int = 5
    epochs: int = 10

    def to_proto(self) -> graph_pb2.Node2VecParameters:
        return graph_pb2.Node2VecParameters(
            ndim=self.dim,
            walk_length=self.walk_length,
            window=self.window,
            p=self.p,
            q=self.q,
            alpha=self.alpha,
            min_alpha=self.min_alpha,
            negative=self.negative,
            epochs=self.epochs,
        )


@dataclasses.dataclass(frozen=True)
class RelationalSpace(Space):
    """Spaces for embeddings that encode relationships."""

    node2vec_params: Node2VecParameters | None = None

    def _sub_orm_objects(self, orm_object: orm.Space) -> Iterable[orm.Base]:
        return []

    @classmethod
    def create(
        cls, feature_view: FeatureView, client: system.Client | None = None
    ) -> Ok[RelationalSpace] | BadArgumentError:
        if not feature_view.relationships:
            return BadArgumentError(
                "space will not be useful without at least one relationship"
            )
        if not feature_view.output_sources:
            return BadArgumentError(
                "space will not be useful without at least one output source"
            )
        orm_self = orm.Space()
        client = client or feature_view.client

        return Ok(RelationalSpace(client, orm_self, SpaceID(), feature_view))

    def with_node2vec(self, params: Node2VecParameters):
        return dataclasses.replace(self, node2vec_params=params)

    def legacy_embeddings_table(self) -> Ok[Table] | BadArgumentError:
        if not self.node2vec_params:
            return BadArgumentError("space was not configured")

        def gen_edge_list_tables():
            for edge_table in self.feature_view.output_edge_tables():
                endpoint_metadata = edge_table.get_typed_metadata(
                    FeatureViewEdgeTableMetadata
                )
                yield op_graph.EdgeListTable(
                    table=edge_table.set_metadata({}).op_graph,
                    start_column_name=endpoint_metadata.start_source_column_name,
                    start_entity_name=endpoint_metadata.start_source_name,
                    end_column_name=endpoint_metadata.end_source_column_name,
                    end_entity_name=endpoint_metadata.end_source_name,
                )

        edge_list_tables = list(gen_edge_list_tables())
        if not edge_list_tables:
            return BadArgumentError(
                "no relationships given, or those given did not result in edges between"
                + "output sources"
            )
        return Ok(
            Table(
                self.client,
                op_graph.op.embed_node2vec_from_edge_lists(
                    edge_list_tables=edge_list_tables,
                    params=self.node2vec_params.to_proto(),
                ),
            )
        )

    def _split_embedding_table_by_source(
        self, embeddings_table: op_graph.Op
    ) -> Ok[Mapping[SourceID, Table]] | BadArgumentError:
        match embeddings_table.unnest_struct("id"):
            case BadArgumentError() as err:
                return err
            case Ok(embeddings_table):
                pass
        id_fields = [
            field
            for field in embeddings_table.schema
            if field.name.startswith("column_")
        ]
        id_fields.sort(key=lambda field: int(field.name.removeprefix("column_")))
        source_name_column = id_fields[-1].name
        dtype_to_id_field = {field.dtype: field.name for field in id_fields[:-1]}

        result = dict[SourceID, Table]()
        for source_id in self.feature_view.output_sources:
            source = Source.from_id(source_id).unwrap_or_raise()
            primary_key_field = source.table.schema.get_primary_key()
            if primary_key_field is None:
                return BadArgumentError(
                    "source is required to have a primary key to be an output"
                )
            source_id_column = dtype_to_id_field[primary_key_field.dtype]
            table = Table(
                self.client,
                embeddings_table.filter_rows(
                    op_graph.row_filter.eq(source_name_column, source.name)
                )
                .select_columns([source_id_column, "embedding"])
                .rename_columns({source_id_column: "entity_id"})
                .add_literal_column("source_id", str(source_id))
                .unwrap_or_raise(),
            )
            result[source_id] = table

        return Ok(result)

    def embeddings_tables(self) -> Ok[Mapping[SourceID, Table]] | BadArgumentError:
        return self.legacy_embeddings_table().and_then(
            lambda t: self._split_embedding_table_by_source(t.op_graph)
        )


@dataclasses.dataclass
class ConcatAndEmbedParameters:
    column_names: list[str]
    model_name: str
    tokenizer_name: str
    expected_vector_length: int
    expected_coordinate_bitwidth: Literal[32, 64] = 32


@dataclasses.dataclass(frozen=True)
class SemanticSpace(Space):
    """Spaces for embedding source properties."""

    output_source: Source
    concat_and_embed_params: ConcatAndEmbedParameters | None = None

    def _sub_orm_objects(self, orm_object: orm.Space) -> Iterable[orm.Base]:
        return []

    @classmethod
    def create(
        cls, feature_view: FeatureView, client: system.Client | None = None
    ) -> Ok[SemanticSpace] | BadArgumentError:
        client = client or feature_view.client
        if len(feature_view.output_sources) != 1:
            return BadArgumentError("feature view must have exactly one output source")
        match Source.from_id(next(iter(feature_view.output_sources)), client=client):
            case NotFoundError() as err:
                return BadArgumentError.from_(err)
            case Ok(output_source):
                pass

        orm_self = orm.Space()
        return Ok(
            SemanticSpace(client, orm_self, SpaceID(), feature_view, output_source)
        )

    def with_concat_and_embed(self, params: ConcatAndEmbedParameters) -> SemanticSpace:
        return dataclasses.replace(self, concat_and_embed_params=params)

    def embeddings_tables(self) -> Ok[Mapping[SourceID, Table]] | BadArgumentError:
        if not self.concat_and_embed_params:
            return BadArgumentError("space was not configured to produce embeddings")
        params: ConcatAndEmbedParameters = self.concat_and_embed_params
        pk_field = self.output_source.table.schema.get_primary_key()
        if not pk_field:
            return BadArgumentError("output source must have a primary key")

        combined_column_tmp_name = f"__concat-{uuid.uuid4()}"
        embedding_column_tmp_name = f"__embed-{uuid.uuid4()}"

        return (
            self.output_source.table.op_graph.concat_string(
                params.column_names,
                combined_column_tmp_name,
                _DEFAULT_CONCAT_SEPARATOR,
            )
            .and_then(
                lambda t: t.embed_column(
                    combined_column_tmp_name,
                    embedding_column_tmp_name,
                    params.model_name,
                    params.tokenizer_name,
                    params.expected_vector_length,
                    params.expected_coordinate_bitwidth,
                )
            )
            .and_then(
                lambda t: t.select_columns([pk_field.name, embedding_column_tmp_name])
                .rename_columns(
                    {pk_field.name: "entity_id", embedding_column_tmp_name: "embedding"}
                )
                .add_literal_column("source_id", str(self.output_source.id))
            )
            .map(lambda t: {self.output_source.id: Table(self.client, t)})
        )
