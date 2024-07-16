"""Base models for corvic RDBMS backed orm tables."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, ClassVar, Protocol, runtime_checkable

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from google.protobuf import timestamp_pb2
from sqlalchemy.ext import hybrid
from typing_extensions import Self

import corvic.result
from corvic.orm._proto_columns import ProtoMessageDecorator
from corvic.orm.func import utc_now
from corvic.orm.keys import (
    ForeignKey,
    MappedPrimaryKey,
    primary_key_identity_column,
    primary_key_uuid_column,
)
from corvic_generated.orm.v1 import common_pb2, feature_view_pb2, space_pb2
from corvic_generated.status.v1 import event_pb2


class Base(sa_orm.MappedAsDataclass, sa_orm.DeclarativeBase):
    """Base class for all DB mapped classes."""

    type_annotation_map: ClassVar = {
        common_pb2.BlobUrlList: ProtoMessageDecorator(common_pb2.BlobUrlList()),
        feature_view_pb2.FeatureViewOutput: ProtoMessageDecorator(
            feature_view_pb2.FeatureViewOutput()
        ),
        common_pb2.EmbeddingMetrics: ProtoMessageDecorator(
            common_pb2.EmbeddingMetrics()
        ),
        space_pb2.SpaceParameters: ProtoMessageDecorator(space_pb2.SpaceParameters()),
    }

    _created_at: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        "created_at", sa.DateTime(timezone=True), server_default=utc_now(), init=False
    )
    _updated_at: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        "updated_at",
        sa.DateTime(timezone=True),
        onupdate=utc_now(),
        server_default=utc_now(),
        init=False,
        nullable=True,
    )

    @hybrid.hybrid_property
    def created_at(self) -> datetime:
        if not self._created_at:
            # If not committed in the database the output should be None.
            # Align the typing to other fields without the None included.
            return None  # pyright: ignore[reportReturnType]
        return self._created_at.replace(tzinfo=timezone.utc)

    @hybrid.hybrid_property
    def updated_at(self) -> datetime:
        if not self._updated_at:
            # If not committed in the database the output should be None.
            # Align the typing to other fields without the None included.
            return None  # pyright: ignore[reportReturnType]
        return self._updated_at.replace(tzinfo=timezone.utc)

    @classmethod
    def foreign_key(cls):
        return ForeignKey(cls=cls)


class OrgBase(Base):
    """An organization it a top level grouping of resources."""

    __tablename__ = "org"

    # overriding table_args is the recommending way of defining these base model types
    __table_args__: ClassVar[Any] = ({"extend_existing": True},)

    id: sa_orm.Mapped[str | None] = primary_key_uuid_column()

    @hybrid.hybrid_property
    def name(self) -> str:
        if self.id is None:
            raise corvic.result.Error(
                "invalid request for the id of an unregistered object"
            )
        return self.id


class EventKey:
    """An event key."""

    @runtime_checkable
    class Provider(Protocol):
        """Type which can provide an event key."""

        @property
        def event_key(self) -> EventKey: ...

    def __init__(self, id: str):
        self._id = id

    def __str__(self):
        return self._id

    @classmethod
    def from_str(cls, id: str) -> Self:
        return cls(id=id)

    @classmethod
    def from_uuid(cls, uuid: uuid.UUID) -> Self:
        return cls(id=str(uuid))

    @property
    def event_key(self):
        return self


class EventBase(Base):
    """Events from corvic orm objects."""

    __tablename__ = "event"

    # overriding table_args is the recommending way of defining these base model types
    __table_args__: ClassVar[Any] = {"extend_existing": True}

    event: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer)
    reason: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text)
    regarding: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text)
    event_key: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text)
    timestamp: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime(timezone=True)
    )
    id: MappedPrimaryKey = primary_key_identity_column()

    @classmethod
    def select_latest_by_event_key(cls, event_key: EventKey, limit: int | None = None):
        query = (
            sa.select(cls)
            .where(cls.event_key == str(event_key))
            .order_by(cls.timestamp.desc())
        )
        if limit:
            query = query.limit(limit)
        return query

    def as_event(self) -> event_pb2.Event:
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(dt=self.timestamp)
        return event_pb2.Event(
            reason=self.reason,
            regarding=self.regarding,
            event_type=event_pb2.EventType.Name(self.event),
            timestamp=timestamp,
        )
