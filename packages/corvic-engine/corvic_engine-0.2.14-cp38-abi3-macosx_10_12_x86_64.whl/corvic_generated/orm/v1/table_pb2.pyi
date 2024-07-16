from buf.validate import validate_pb2 as _validate_pb2
from corvic_generated.algorithm.graph.v1 import graph_pb2 as _graph_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JoinType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JOIN_TYPE_UNSPECIFIED: _ClassVar[JoinType]
    JOIN_TYPE_INNER: _ClassVar[JoinType]
    JOIN_TYPE_LEFT_OUTER: _ClassVar[JoinType]

class AggregationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AGGREGATION_TYPE_UNSPECIFIED: _ClassVar[AggregationType]
    AGGREGATION_TYPE_COUNT: _ClassVar[AggregationType]
    AGGREGATION_TYPE_AVG: _ClassVar[AggregationType]
    AGGREGATION_TYPE_MODE: _ClassVar[AggregationType]
    AGGREGATION_TYPE_MIN: _ClassVar[AggregationType]
    AGGREGATION_TYPE_MAX: _ClassVar[AggregationType]
    AGGREGATION_TYPE_SUM: _ClassVar[AggregationType]

class LogicalCombination(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOGICAL_COMBINATION_UNSPECIFIED: _ClassVar[LogicalCombination]
    LOGICAL_COMBINATION_ANY: _ClassVar[LogicalCombination]
    LOGICAL_COMBINATION_ALL: _ClassVar[LogicalCombination]

class ComparisonType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COMPARISON_TYPE_UNSPECIFIED: _ClassVar[ComparisonType]
    COMPARISON_TYPE_EQ: _ClassVar[ComparisonType]
    COMPARISON_TYPE_NE: _ClassVar[ComparisonType]
    COMPARISON_TYPE_LT: _ClassVar[ComparisonType]
    COMPARISON_TYPE_GT: _ClassVar[ComparisonType]
    COMPARISON_TYPE_LE: _ClassVar[ComparisonType]
    COMPARISON_TYPE_GE: _ClassVar[ComparisonType]

class FloatBitWidth(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FLOAT_BIT_WIDTH_UNSPECIFIED: _ClassVar[FloatBitWidth]
    FLOAT_BIT_WIDTH_32: _ClassVar[FloatBitWidth]
    FLOAT_BIT_WIDTH_64: _ClassVar[FloatBitWidth]
JOIN_TYPE_UNSPECIFIED: JoinType
JOIN_TYPE_INNER: JoinType
JOIN_TYPE_LEFT_OUTER: JoinType
AGGREGATION_TYPE_UNSPECIFIED: AggregationType
AGGREGATION_TYPE_COUNT: AggregationType
AGGREGATION_TYPE_AVG: AggregationType
AGGREGATION_TYPE_MODE: AggregationType
AGGREGATION_TYPE_MIN: AggregationType
AGGREGATION_TYPE_MAX: AggregationType
AGGREGATION_TYPE_SUM: AggregationType
LOGICAL_COMBINATION_UNSPECIFIED: LogicalCombination
LOGICAL_COMBINATION_ANY: LogicalCombination
LOGICAL_COMBINATION_ALL: LogicalCombination
COMPARISON_TYPE_UNSPECIFIED: ComparisonType
COMPARISON_TYPE_EQ: ComparisonType
COMPARISON_TYPE_NE: ComparisonType
COMPARISON_TYPE_LT: ComparisonType
COMPARISON_TYPE_GT: ComparisonType
COMPARISON_TYPE_LE: ComparisonType
COMPARISON_TYPE_GE: ComparisonType
FLOAT_BIT_WIDTH_UNSPECIFIED: FloatBitWidth
FLOAT_BIT_WIDTH_32: FloatBitWidth
FLOAT_BIT_WIDTH_64: FloatBitWidth

class TableComputeOp(_message.Message):
    __slots__ = ("empty", "select_from_staging", "rename_columns", "join", "select_columns", "limit_rows", "order_by", "filter_rows", "distinct_rows", "update_metadata", "set_metadata", "remove_from_metadata", "update_feature_types", "rollup_by_aggregation", "embed_node2vec_from_edge_lists", "embedding_metrics", "embedding_coordinates", "read_from_parquet", "select_from_vector_staging", "concat", "unnest_struct", "nest_into_struct", "add_literal_column", "combine_columns", "embed_column")
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    SELECT_FROM_STAGING_FIELD_NUMBER: _ClassVar[int]
    RENAME_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    JOIN_FIELD_NUMBER: _ClassVar[int]
    SELECT_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    LIMIT_ROWS_FIELD_NUMBER: _ClassVar[int]
    ORDER_BY_FIELD_NUMBER: _ClassVar[int]
    FILTER_ROWS_FIELD_NUMBER: _ClassVar[int]
    DISTINCT_ROWS_FIELD_NUMBER: _ClassVar[int]
    UPDATE_METADATA_FIELD_NUMBER: _ClassVar[int]
    SET_METADATA_FIELD_NUMBER: _ClassVar[int]
    REMOVE_FROM_METADATA_FIELD_NUMBER: _ClassVar[int]
    UPDATE_FEATURE_TYPES_FIELD_NUMBER: _ClassVar[int]
    ROLLUP_BY_AGGREGATION_FIELD_NUMBER: _ClassVar[int]
    EMBED_NODE2VEC_FROM_EDGE_LISTS_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_METRICS_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    READ_FROM_PARQUET_FIELD_NUMBER: _ClassVar[int]
    SELECT_FROM_VECTOR_STAGING_FIELD_NUMBER: _ClassVar[int]
    CONCAT_FIELD_NUMBER: _ClassVar[int]
    UNNEST_STRUCT_FIELD_NUMBER: _ClassVar[int]
    NEST_INTO_STRUCT_FIELD_NUMBER: _ClassVar[int]
    ADD_LITERAL_COLUMN_FIELD_NUMBER: _ClassVar[int]
    COMBINE_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    EMBED_COLUMN_FIELD_NUMBER: _ClassVar[int]
    empty: EmptyOp
    select_from_staging: SelectFromStagingOp
    rename_columns: RenameColumnsOp
    join: JoinOp
    select_columns: SelectColumnsOp
    limit_rows: LimitRowsOp
    order_by: OrderByOp
    filter_rows: FilterRowsOp
    distinct_rows: DistinctRowsOp
    update_metadata: UpdateMetadataOp
    set_metadata: SetMetadataOp
    remove_from_metadata: RemoveFromMetadataOp
    update_feature_types: UpdateFeatureTypesOp
    rollup_by_aggregation: RollupByAggregationOp
    embed_node2vec_from_edge_lists: EmbedNode2vecFromEdgeListsOp
    embedding_metrics: EmbeddingMetricsOp
    embedding_coordinates: EmbeddingCoordinatesOp
    read_from_parquet: ReadFromParquetOp
    select_from_vector_staging: SelectFromVectorStagingOp
    concat: ConcatOp
    unnest_struct: UnnestStructOp
    nest_into_struct: NestIntoStructOp
    add_literal_column: AddLiteralColumnOp
    combine_columns: CombineColumnsOp
    embed_column: EmbedColumnOp
    def __init__(self, empty: _Optional[_Union[EmptyOp, _Mapping]] = ..., select_from_staging: _Optional[_Union[SelectFromStagingOp, _Mapping]] = ..., rename_columns: _Optional[_Union[RenameColumnsOp, _Mapping]] = ..., join: _Optional[_Union[JoinOp, _Mapping]] = ..., select_columns: _Optional[_Union[SelectColumnsOp, _Mapping]] = ..., limit_rows: _Optional[_Union[LimitRowsOp, _Mapping]] = ..., order_by: _Optional[_Union[OrderByOp, _Mapping]] = ..., filter_rows: _Optional[_Union[FilterRowsOp, _Mapping]] = ..., distinct_rows: _Optional[_Union[DistinctRowsOp, _Mapping]] = ..., update_metadata: _Optional[_Union[UpdateMetadataOp, _Mapping]] = ..., set_metadata: _Optional[_Union[SetMetadataOp, _Mapping]] = ..., remove_from_metadata: _Optional[_Union[RemoveFromMetadataOp, _Mapping]] = ..., update_feature_types: _Optional[_Union[UpdateFeatureTypesOp, _Mapping]] = ..., rollup_by_aggregation: _Optional[_Union[RollupByAggregationOp, _Mapping]] = ..., embed_node2vec_from_edge_lists: _Optional[_Union[EmbedNode2vecFromEdgeListsOp, _Mapping]] = ..., embedding_metrics: _Optional[_Union[EmbeddingMetricsOp, _Mapping]] = ..., embedding_coordinates: _Optional[_Union[EmbeddingCoordinatesOp, _Mapping]] = ..., read_from_parquet: _Optional[_Union[ReadFromParquetOp, _Mapping]] = ..., select_from_vector_staging: _Optional[_Union[SelectFromVectorStagingOp, _Mapping]] = ..., concat: _Optional[_Union[ConcatOp, _Mapping]] = ..., unnest_struct: _Optional[_Union[UnnestStructOp, _Mapping]] = ..., nest_into_struct: _Optional[_Union[NestIntoStructOp, _Mapping]] = ..., add_literal_column: _Optional[_Union[AddLiteralColumnOp, _Mapping]] = ..., combine_columns: _Optional[_Union[CombineColumnsOp, _Mapping]] = ..., embed_column: _Optional[_Union[EmbedColumnOp, _Mapping]] = ...) -> None: ...

class JoinOp(_message.Message):
    __slots__ = ("left_source", "left_join_columns", "right_source", "right_join_columns", "how")
    LEFT_SOURCE_FIELD_NUMBER: _ClassVar[int]
    LEFT_JOIN_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    RIGHT_SOURCE_FIELD_NUMBER: _ClassVar[int]
    RIGHT_JOIN_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    HOW_FIELD_NUMBER: _ClassVar[int]
    left_source: TableComputeOp
    left_join_columns: _containers.RepeatedScalarFieldContainer[str]
    right_source: TableComputeOp
    right_join_columns: _containers.RepeatedScalarFieldContainer[str]
    how: JoinType
    def __init__(self, left_source: _Optional[_Union[TableComputeOp, _Mapping]] = ..., left_join_columns: _Optional[_Iterable[str]] = ..., right_source: _Optional[_Union[TableComputeOp, _Mapping]] = ..., right_join_columns: _Optional[_Iterable[str]] = ..., how: _Optional[_Union[JoinType, str]] = ...) -> None: ...

class RenameColumnsOp(_message.Message):
    __slots__ = ("source", "old_names_to_new")
    class OldNamesToNewEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    OLD_NAMES_TO_NEW_FIELD_NUMBER: _ClassVar[int]
    source: TableComputeOp
    old_names_to_new: _containers.ScalarMap[str, str]
    def __init__(self, source: _Optional[_Union[TableComputeOp, _Mapping]] = ..., old_names_to_new: _Optional[_Mapping[str, str]] = ...) -> None: ...

class TextFeatureType(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CategoricalFeatureType(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PrimaryKeyFeatureType(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ForeignKeyFeatureType(_message.Message):
    __slots__ = ("referenced_source_id",)
    REFERENCED_SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    referenced_source_id: str
    def __init__(self, referenced_source_id: _Optional[str] = ...) -> None: ...

class IdentifierFeatureType(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class NumericalFeatureType(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MultiCategoricalFeatureType(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TimestampFeatureType(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class EmbeddingFeatureType(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownFeatureType(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FeatureType(_message.Message):
    __slots__ = ("text", "categorical", "primary_key", "foreign_key", "identifier", "numerical", "multi_categorical", "timestamp", "embedding", "unknown", "is_excluded")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    CATEGORICAL_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_KEY_FIELD_NUMBER: _ClassVar[int]
    FOREIGN_KEY_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    NUMERICAL_FIELD_NUMBER: _ClassVar[int]
    MULTI_CATEGORICAL_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FIELD_NUMBER: _ClassVar[int]
    IS_EXCLUDED_FIELD_NUMBER: _ClassVar[int]
    text: TextFeatureType
    categorical: CategoricalFeatureType
    primary_key: PrimaryKeyFeatureType
    foreign_key: ForeignKeyFeatureType
    identifier: IdentifierFeatureType
    numerical: NumericalFeatureType
    multi_categorical: MultiCategoricalFeatureType
    timestamp: TimestampFeatureType
    embedding: EmbeddingFeatureType
    unknown: UnknownFeatureType
    is_excluded: bool
    def __init__(self, text: _Optional[_Union[TextFeatureType, _Mapping]] = ..., categorical: _Optional[_Union[CategoricalFeatureType, _Mapping]] = ..., primary_key: _Optional[_Union[PrimaryKeyFeatureType, _Mapping]] = ..., foreign_key: _Optional[_Union[ForeignKeyFeatureType, _Mapping]] = ..., identifier: _Optional[_Union[IdentifierFeatureType, _Mapping]] = ..., numerical: _Optional[_Union[NumericalFeatureType, _Mapping]] = ..., multi_categorical: _Optional[_Union[MultiCategoricalFeatureType, _Mapping]] = ..., timestamp: _Optional[_Union[TimestampFeatureType, _Mapping]] = ..., embedding: _Optional[_Union[EmbeddingFeatureType, _Mapping]] = ..., unknown: _Optional[_Union[UnknownFeatureType, _Mapping]] = ..., is_excluded: bool = ...) -> None: ...

class SelectFromStagingOp(_message.Message):
    __slots__ = ("blob_names", "expected_rows", "arrow_schema", "feature_types")
    BLOB_NAMES_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_ROWS_FIELD_NUMBER: _ClassVar[int]
    ARROW_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    FEATURE_TYPES_FIELD_NUMBER: _ClassVar[int]
    blob_names: _containers.RepeatedScalarFieldContainer[str]
    expected_rows: int
    arrow_schema: bytes
    feature_types: _containers.RepeatedCompositeFieldContainer[FeatureType]
    def __init__(self, blob_names: _Optional[_Iterable[str]] = ..., expected_rows: _Optional[int] = ..., arrow_schema: _Optional[bytes] = ..., feature_types: _Optional[_Iterable[_Union[FeatureType, _Mapping]]] = ...) -> None: ...

class SelectColumnsOp(_message.Message):
    __slots__ = ("source", "columns")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    source: TableComputeOp
    columns: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, source: _Optional[_Union[TableComputeOp, _Mapping]] = ..., columns: _Optional[_Iterable[str]] = ...) -> None: ...

class LimitRowsOp(_message.Message):
    __slots__ = ("source", "num_rows")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    NUM_ROWS_FIELD_NUMBER: _ClassVar[int]
    source: TableComputeOp
    num_rows: int
    def __init__(self, source: _Optional[_Union[TableComputeOp, _Mapping]] = ..., num_rows: _Optional[int] = ...) -> None: ...

class OrderByOp(_message.Message):
    __slots__ = ("source", "columns", "desc")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    DESC_FIELD_NUMBER: _ClassVar[int]
    source: TableComputeOp
    columns: _containers.RepeatedScalarFieldContainer[str]
    desc: bool
    def __init__(self, source: _Optional[_Union[TableComputeOp, _Mapping]] = ..., columns: _Optional[_Iterable[str]] = ..., desc: bool = ...) -> None: ...

class FilterRowsOp(_message.Message):
    __slots__ = ("source", "row_filter")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    ROW_FILTER_FIELD_NUMBER: _ClassVar[int]
    source: TableComputeOp
    row_filter: RowFilter
    def __init__(self, source: _Optional[_Union[TableComputeOp, _Mapping]] = ..., row_filter: _Optional[_Union[RowFilter, _Mapping]] = ...) -> None: ...

class DistinctRowsOp(_message.Message):
    __slots__ = ("source",)
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    source: TableComputeOp
    def __init__(self, source: _Optional[_Union[TableComputeOp, _Mapping]] = ...) -> None: ...

class UpdateMetadataOp(_message.Message):
    __slots__ = ("source", "metadata_updates")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    METADATA_UPDATES_FIELD_NUMBER: _ClassVar[int]
    source: TableComputeOp
    metadata_updates: _struct_pb2.Struct
    def __init__(self, source: _Optional[_Union[TableComputeOp, _Mapping]] = ..., metadata_updates: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class SetMetadataOp(_message.Message):
    __slots__ = ("source", "new_metadata")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    NEW_METADATA_FIELD_NUMBER: _ClassVar[int]
    source: TableComputeOp
    new_metadata: _struct_pb2.Struct
    def __init__(self, source: _Optional[_Union[TableComputeOp, _Mapping]] = ..., new_metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class RemoveFromMetadataOp(_message.Message):
    __slots__ = ("source", "keys_to_remove")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    KEYS_TO_REMOVE_FIELD_NUMBER: _ClassVar[int]
    source: TableComputeOp
    keys_to_remove: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, source: _Optional[_Union[TableComputeOp, _Mapping]] = ..., keys_to_remove: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateFeatureTypesOp(_message.Message):
    __slots__ = ("source", "new_feature_types")
    class NewFeatureTypesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: FeatureType
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[FeatureType, _Mapping]] = ...) -> None: ...
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    NEW_FEATURE_TYPES_FIELD_NUMBER: _ClassVar[int]
    source: TableComputeOp
    new_feature_types: _containers.MessageMap[str, FeatureType]
    def __init__(self, source: _Optional[_Union[TableComputeOp, _Mapping]] = ..., new_feature_types: _Optional[_Mapping[str, FeatureType]] = ...) -> None: ...

class RollupByAggregationOp(_message.Message):
    __slots__ = ("source", "group_by_column_names", "target_column_name", "aggregation_type")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    GROUP_BY_COLUMN_NAMES_FIELD_NUMBER: _ClassVar[int]
    TARGET_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    source: TableComputeOp
    group_by_column_names: _containers.RepeatedScalarFieldContainer[str]
    target_column_name: str
    aggregation_type: AggregationType
    def __init__(self, source: _Optional[_Union[TableComputeOp, _Mapping]] = ..., group_by_column_names: _Optional[_Iterable[str]] = ..., target_column_name: _Optional[str] = ..., aggregation_type: _Optional[_Union[AggregationType, str]] = ...) -> None: ...

class CombineFiltersRowFilter(_message.Message):
    __slots__ = ("row_filters", "logical_combination")
    ROW_FILTERS_FIELD_NUMBER: _ClassVar[int]
    LOGICAL_COMBINATION_FIELD_NUMBER: _ClassVar[int]
    row_filters: _containers.RepeatedCompositeFieldContainer[RowFilter]
    logical_combination: LogicalCombination
    def __init__(self, row_filters: _Optional[_Iterable[_Union[RowFilter, _Mapping]]] = ..., logical_combination: _Optional[_Union[LogicalCombination, str]] = ...) -> None: ...

class CompareColumnToLiteralRowFilter(_message.Message):
    __slots__ = ("column_name", "literal", "comparison_type")
    COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    LITERAL_FIELD_NUMBER: _ClassVar[int]
    COMPARISON_TYPE_FIELD_NUMBER: _ClassVar[int]
    column_name: str
    literal: _struct_pb2.Value
    comparison_type: ComparisonType
    def __init__(self, column_name: _Optional[str] = ..., literal: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ..., comparison_type: _Optional[_Union[ComparisonType, str]] = ...) -> None: ...

class RowFilter(_message.Message):
    __slots__ = ("compare_column_to_literal", "combine_filters")
    COMPARE_COLUMN_TO_LITERAL_FIELD_NUMBER: _ClassVar[int]
    COMBINE_FILTERS_FIELD_NUMBER: _ClassVar[int]
    compare_column_to_literal: CompareColumnToLiteralRowFilter
    combine_filters: CombineFiltersRowFilter
    def __init__(self, compare_column_to_literal: _Optional[_Union[CompareColumnToLiteralRowFilter, _Mapping]] = ..., combine_filters: _Optional[_Union[CombineFiltersRowFilter, _Mapping]] = ...) -> None: ...

class EmptyOp(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class EdgeListTable(_message.Message):
    __slots__ = ("table", "start_column_name", "end_column_name", "start_entity_name", "end_entity_name")
    TABLE_FIELD_NUMBER: _ClassVar[int]
    START_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    END_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    START_ENTITY_NAME_FIELD_NUMBER: _ClassVar[int]
    END_ENTITY_NAME_FIELD_NUMBER: _ClassVar[int]
    table: TableComputeOp
    start_column_name: str
    end_column_name: str
    start_entity_name: str
    end_entity_name: str
    def __init__(self, table: _Optional[_Union[TableComputeOp, _Mapping]] = ..., start_column_name: _Optional[str] = ..., end_column_name: _Optional[str] = ..., start_entity_name: _Optional[str] = ..., end_entity_name: _Optional[str] = ...) -> None: ...

class EmbedNode2vecFromEdgeListsOp(_message.Message):
    __slots__ = ("edge_list_tables", "node2vec_parameters")
    EDGE_LIST_TABLES_FIELD_NUMBER: _ClassVar[int]
    NODE2VEC_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    edge_list_tables: _containers.RepeatedCompositeFieldContainer[EdgeListTable]
    node2vec_parameters: _graph_pb2.Node2VecParameters
    def __init__(self, edge_list_tables: _Optional[_Iterable[_Union[EdgeListTable, _Mapping]]] = ..., node2vec_parameters: _Optional[_Union[_graph_pb2.Node2VecParameters, _Mapping]] = ...) -> None: ...

class EmbeddingMetricsOp(_message.Message):
    __slots__ = ("table", "embedding_column_name")
    TABLE_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    table: TableComputeOp
    embedding_column_name: str
    def __init__(self, table: _Optional[_Union[TableComputeOp, _Mapping]] = ..., embedding_column_name: _Optional[str] = ...) -> None: ...

class EmbeddingCoordinatesOp(_message.Message):
    __slots__ = ("table", "n_components", "metric", "embedding_column_name")
    TABLE_FIELD_NUMBER: _ClassVar[int]
    N_COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    METRIC_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    table: TableComputeOp
    n_components: int
    metric: str
    embedding_column_name: str
    def __init__(self, table: _Optional[_Union[TableComputeOp, _Mapping]] = ..., n_components: _Optional[int] = ..., metric: _Optional[str] = ..., embedding_column_name: _Optional[str] = ...) -> None: ...

class ReadFromParquetOp(_message.Message):
    __slots__ = ("blob_names", "expected_rows", "arrow_schema", "feature_types")
    BLOB_NAMES_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_ROWS_FIELD_NUMBER: _ClassVar[int]
    ARROW_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    FEATURE_TYPES_FIELD_NUMBER: _ClassVar[int]
    blob_names: _containers.RepeatedScalarFieldContainer[str]
    expected_rows: int
    arrow_schema: bytes
    feature_types: _containers.RepeatedCompositeFieldContainer[FeatureType]
    def __init__(self, blob_names: _Optional[_Iterable[str]] = ..., expected_rows: _Optional[int] = ..., arrow_schema: _Optional[bytes] = ..., feature_types: _Optional[_Iterable[_Union[FeatureType, _Mapping]]] = ...) -> None: ...

class SelectFromVectorStagingOp(_message.Message):
    __slots__ = ("input_vector", "blob_names", "similarity_metric", "vector_column_name", "num_results", "arrow_schema", "feature_types")
    INPUT_VECTOR_FIELD_NUMBER: _ClassVar[int]
    BLOB_NAMES_FIELD_NUMBER: _ClassVar[int]
    SIMILARITY_METRIC_FIELD_NUMBER: _ClassVar[int]
    VECTOR_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    NUM_RESULTS_FIELD_NUMBER: _ClassVar[int]
    ARROW_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    FEATURE_TYPES_FIELD_NUMBER: _ClassVar[int]
    input_vector: _containers.RepeatedScalarFieldContainer[float]
    blob_names: _containers.RepeatedScalarFieldContainer[str]
    similarity_metric: str
    vector_column_name: str
    num_results: int
    arrow_schema: bytes
    feature_types: _containers.RepeatedCompositeFieldContainer[FeatureType]
    def __init__(self, input_vector: _Optional[_Iterable[float]] = ..., blob_names: _Optional[_Iterable[str]] = ..., similarity_metric: _Optional[str] = ..., vector_column_name: _Optional[str] = ..., num_results: _Optional[int] = ..., arrow_schema: _Optional[bytes] = ..., feature_types: _Optional[_Iterable[_Union[FeatureType, _Mapping]]] = ...) -> None: ...

class ConcatOp(_message.Message):
    __slots__ = ("tables",)
    TABLES_FIELD_NUMBER: _ClassVar[int]
    tables: _containers.RepeatedCompositeFieldContainer[TableComputeOp]
    def __init__(self, tables: _Optional[_Iterable[_Union[TableComputeOp, _Mapping]]] = ...) -> None: ...

class UnnestStructOp(_message.Message):
    __slots__ = ("source", "struct_column_name")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    STRUCT_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    source: TableComputeOp
    struct_column_name: str
    def __init__(self, source: _Optional[_Union[TableComputeOp, _Mapping]] = ..., struct_column_name: _Optional[str] = ...) -> None: ...

class NestIntoStructOp(_message.Message):
    __slots__ = ("source", "struct_column_name", "column_names_to_nest")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    STRUCT_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    COLUMN_NAMES_TO_NEST_FIELD_NUMBER: _ClassVar[int]
    source: TableComputeOp
    struct_column_name: str
    column_names_to_nest: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, source: _Optional[_Union[TableComputeOp, _Mapping]] = ..., struct_column_name: _Optional[str] = ..., column_names_to_nest: _Optional[_Iterable[str]] = ...) -> None: ...

class AddLiteralColumnOp(_message.Message):
    __slots__ = ("source", "literal", "column_arrow_schema", "column_feature_type")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    LITERAL_FIELD_NUMBER: _ClassVar[int]
    COLUMN_ARROW_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    COLUMN_FEATURE_TYPE_FIELD_NUMBER: _ClassVar[int]
    source: TableComputeOp
    literal: _struct_pb2.Value
    column_arrow_schema: bytes
    column_feature_type: FeatureType
    def __init__(self, source: _Optional[_Union[TableComputeOp, _Mapping]] = ..., literal: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ..., column_arrow_schema: _Optional[bytes] = ..., column_feature_type: _Optional[_Union[FeatureType, _Mapping]] = ...) -> None: ...

class ConcatString(_message.Message):
    __slots__ = ("separator",)
    SEPARATOR_FIELD_NUMBER: _ClassVar[int]
    separator: str
    def __init__(self, separator: _Optional[str] = ...) -> None: ...

class CombineColumnsOp(_message.Message):
    __slots__ = ("source", "column_names", "combined_column_name", "concat_string")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_NAMES_FIELD_NUMBER: _ClassVar[int]
    COMBINED_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    CONCAT_STRING_FIELD_NUMBER: _ClassVar[int]
    source: TableComputeOp
    column_names: _containers.RepeatedScalarFieldContainer[str]
    combined_column_name: str
    concat_string: ConcatString
    def __init__(self, source: _Optional[_Union[TableComputeOp, _Mapping]] = ..., column_names: _Optional[_Iterable[str]] = ..., combined_column_name: _Optional[str] = ..., concat_string: _Optional[_Union[ConcatString, _Mapping]] = ...) -> None: ...

class EmbedColumnOp(_message.Message):
    __slots__ = ("source", "column_name", "embedding_column_name", "model_name", "tokenizer_name", "expected_vector_length", "expected_coordinate_bitwidth")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    TOKENIZER_NAME_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_VECTOR_LENGTH_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_COORDINATE_BITWIDTH_FIELD_NUMBER: _ClassVar[int]
    source: TableComputeOp
    column_name: str
    embedding_column_name: str
    model_name: str
    tokenizer_name: str
    expected_vector_length: int
    expected_coordinate_bitwidth: FloatBitWidth
    def __init__(self, source: _Optional[_Union[TableComputeOp, _Mapping]] = ..., column_name: _Optional[str] = ..., embedding_column_name: _Optional[str] = ..., model_name: _Optional[str] = ..., tokenizer_name: _Optional[str] = ..., expected_vector_length: _Optional[int] = ..., expected_coordinate_bitwidth: _Optional[_Union[FloatBitWidth, str]] = ...) -> None: ...

class TableSliceArgs(_message.Message):
    __slots__ = ("offset", "length")
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    offset: int
    length: int
    def __init__(self, offset: _Optional[int] = ..., length: _Optional[int] = ...) -> None: ...

class TableComputeContext(_message.Message):
    __slots__ = ("table", "output_url_prefix", "sql_output_slice_args")
    TABLE_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_URL_PREFIX_FIELD_NUMBER: _ClassVar[int]
    SQL_OUTPUT_SLICE_ARGS_FIELD_NUMBER: _ClassVar[int]
    table: TableComputeOp
    output_url_prefix: str
    sql_output_slice_args: TableSliceArgs
    def __init__(self, table: _Optional[_Union[TableComputeOp, _Mapping]] = ..., output_url_prefix: _Optional[str] = ..., sql_output_slice_args: _Optional[_Union[TableSliceArgs, _Mapping]] = ...) -> None: ...

class TableComputeResult(_message.Message):
    __slots__ = ("result_urls", "metrics")
    RESULT_URLS_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    result_urls: _containers.RepeatedScalarFieldContainer[str]
    metrics: _struct_pb2.Struct
    def __init__(self, result_urls: _Optional[_Iterable[str]] = ..., metrics: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class ExecuteRequest(_message.Message):
    __slots__ = ("tables_to_compute",)
    TABLES_TO_COMPUTE_FIELD_NUMBER: _ClassVar[int]
    tables_to_compute: _containers.RepeatedCompositeFieldContainer[TableComputeContext]
    def __init__(self, tables_to_compute: _Optional[_Iterable[_Union[TableComputeContext, _Mapping]]] = ...) -> None: ...

class ExecuteResponse(_message.Message):
    __slots__ = ("table_results",)
    TABLE_RESULTS_FIELD_NUMBER: _ClassVar[int]
    table_results: _containers.RepeatedCompositeFieldContainer[TableComputeResult]
    def __init__(self, table_results: _Optional[_Iterable[_Union[TableComputeResult, _Mapping]]] = ...) -> None: ...

class StreamExecuteRequest(_message.Message):
    __slots__ = ("table_to_compute",)
    TABLE_TO_COMPUTE_FIELD_NUMBER: _ClassVar[int]
    table_to_compute: TableComputeContext
    def __init__(self, table_to_compute: _Optional[_Union[TableComputeContext, _Mapping]] = ...) -> None: ...

class StreamExecuteResponse(_message.Message):
    __slots__ = ("table_results",)
    TABLE_RESULTS_FIELD_NUMBER: _ClassVar[int]
    table_results: _containers.RepeatedCompositeFieldContainer[TableComputeResult]
    def __init__(self, table_results: _Optional[_Iterable[_Union[TableComputeResult, _Mapping]]] = ...) -> None: ...
