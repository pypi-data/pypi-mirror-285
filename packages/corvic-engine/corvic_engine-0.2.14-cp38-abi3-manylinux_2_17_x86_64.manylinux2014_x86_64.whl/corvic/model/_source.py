"""Sources."""

from __future__ import annotations

import dataclasses
import enum
import functools
from collections.abc import Iterable, Mapping
from typing import Final, TypeAlias

import polars as pl
import sqlalchemy.orm as sa_orm
import structlog
from typing_extensions import Self

from corvic import orm, system
from corvic.model._defaults import get_default_client
from corvic.model._resource import Resource
from corvic.model._wrapped_orm import WrappedOrmObject
from corvic.result import BadArgumentError, NotFoundError, Ok
from corvic.table import FeatureType, Table

_logger = structlog.get_logger()

SourceID: TypeAlias = orm.SourceID


@enum.unique
class SourceType(enum.Enum):
    """Hints about how a source should be treated."""

    UNKNOWN = 1
    DIMENSION_TABLE = 2
    FACT_TABLE = 3

    # Work-around missing StrEnum in python 3.10

    @classmethod
    def from_str(cls, value: str):
        match value:
            case "unknown":
                return cls.UNKNOWN
            case "dimension_table":
                return cls.DIMENSION_TABLE
            case "fact_table":
                return cls.FACT_TABLE
            case _:
                raise BadArgumentError(
                    "could not parse value into SourceType", value=value
                )

    def __str__(self):
        """Convert SourceType to readable value."""
        match self:
            case SourceType.UNKNOWN:
                return "unknown"
            case SourceType.DIMENSION_TABLE:
                return "dimension_table"
            case SourceType.FACT_TABLE:
                return "fact_table"


@dataclasses.dataclass(frozen=True)
class Source(WrappedOrmObject[SourceID, orm.Source]):
    """Sources describe how resources should be treated.

    Example:
    >>> Source.from_polars(order_data)
    >>>    .as_dimension_table()
    >>> )
    """

    _SOURCE_TYPE_METADATA_KEY: Final = "source_type"

    @classmethod
    def from_id(
        cls, source_id: SourceID, client: system.Client | None = None
    ) -> Ok[Source] | NotFoundError:
        client = client or get_default_client()
        with sa_orm.Session(client.sa_engine, expire_on_commit=False) as session:
            orm_self = session.get(orm.Source, source_id.to_orm().unwrap_or_raise())

        if orm_self is None:
            return NotFoundError(
                "source with given id does not exists", id=str(source_id)
            )
        return Ok(cls(client, orm_self, SourceID.from_orm(orm_self.id)))

    def _sub_orm_objects(self, orm_object: orm.Source) -> Iterable[orm.Base]:
        yield from orm_object.resource_associations

    @classmethod
    def from_resource(
        cls,
        resource: Resource,
        name: str | None = None,
        client: system.Client | None = None,
        room_id: orm.RoomID | None = None,
    ) -> Ok[Self] | system.DataMisplacedError | BadArgumentError:
        client = client or resource.client
        room_id = room_id or resource.room_id
        match Table.from_parquet_file(client, resource.url):
            case Ok(table):
                pass
            case system.DataMisplacedError() as error:
                return error
            case BadArgumentError() as error:
                return error

        orm_source = orm.Source(
            name=name or resource.name,
            table_op_graph=table.op_graph.to_bytes(),
            resource_associations=[
                orm.SourceResourceAssociation(
                    resource_id=resource.id.to_orm().unwrap_or_raise()
                )
            ],
            room_id=room_id.to_orm().unwrap_or_raise(),
        )

        return Ok(cls(client, orm_source, SourceID()))

    @classmethod
    def from_polars(
        cls,
        name: str,
        data_frame: pl.DataFrame,
        client: system.Client | None = None,
        room_id: orm.RoomID | None = None,
    ) -> Self:
        """Create a source from a pl.DataFrame.

        Args:
            name: a unique name for this source
            data_frame: a polars DataFrame
            client: use a particular system.Client instead of the default
            room_id: room to associate this source with. Use the default room if None.
        """
        client = client or get_default_client()
        resource = Resource.from_polars(data_frame, client).register()
        return cls.from_resource(
            resource, name=name, client=client, room_id=room_id
        ).unwrap_or_raise()

    def _with_new_table(self, table: Table) -> Source:
        orm_source = dataclasses.replace(self.orm_self)
        orm_source.table_op_graph = table.op_graph.to_bytes()
        return Source(self.client, orm_source, self.derived_from_id)

    def with_feature_types(self, feature_types: Mapping[str, FeatureType]) -> Source:
        """Assign a Feature Type to each column in source.

        Args:
            feature_types: Mapping between column name and feature type

        Example:
        >>> with_feature_types(
        >>>        {
        >>>            "id": corvic.table.feature_type.primary_key(),
        >>>            "customer_id": corvic.table.feature_type.foreign_key(
        >>>                customer_source.id
        >>>            ),
        >>>        },
        >>>    )
        """
        return self._with_new_table(self.table.update_feature_types(feature_types))

    @functools.cached_property
    def table(self):
        return Table.from_bytes(self.client, self.orm_self.table_op_graph)

    @property
    def source_type(self) -> SourceType:
        value: str = self.table.metadata.get(
            self._SOURCE_TYPE_METADATA_KEY, str(SourceType.UNKNOWN)
        )
        try:
            return SourceType.from_str(value)
        except (BadArgumentError, ValueError) as exc:
            _logger.exception(
                "returning default source type: failed to parse from table metadata",
                source_id=self.id,
                exc_info=exc,
            )

        return SourceType.UNKNOWN

    @property
    def name(self) -> str:
        return self.orm_self.name

    def as_dimension_table(self) -> Source:
        """Return Source as a Dimension Table."""
        new_table = self.table.update_metadata(
            {self._SOURCE_TYPE_METADATA_KEY: str(SourceType.DIMENSION_TABLE)}
        )
        return self._with_new_table(new_table)

    def as_fact_table(self) -> Source:
        """Return Source as a Fact Table."""
        new_table = self.table.update_metadata(
            {self._SOURCE_TYPE_METADATA_KEY: str(SourceType.FACT_TABLE)}
        )
        return self._with_new_table(new_table)
