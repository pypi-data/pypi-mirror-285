"""Id containers for orm objects."""

import abc
from typing import Generic, TypeVar

from typing_extensions import Self

import corvic.context
from corvic.orm.errors import InvalidORMIdentifierError
from corvic.result import Ok

ORMIdentifier = TypeVar("ORMIdentifier")


class BaseID(Generic[ORMIdentifier], abc.ABC):
    """Base class for all API object identifiers."""

    _value: str

    def __init__(self, value: str = ""):
        self._value = value

    def __str__(self):
        """Directly calling str() is the preferred method for converting to str."""
        return self._value

    def __bool__(self):
        """An ID is truthy if it's not empty."""
        return bool(self._value)

    def __eq__(self, other: object):
        """IDs are equal if they have the same specific type and their values match."""
        if isinstance(other, type(self)):
            return self._value == other._value
        return False

    def __hash__(self):
        """Hash value is exactly the hash of the string."""
        return hash(self._value)

    @abc.abstractmethod
    def to_orm(self) -> Ok[ORMIdentifier] | InvalidORMIdentifierError:
        """Translate this identifier to its orm equivalent."""

    @classmethod
    @abc.abstractmethod
    def from_orm(cls, orm_id: ORMIdentifier | None) -> Self:
        """Make an identifier from some orm identifier."""


class BaseIDFromInt(BaseID[int]):
    """Implementation of BaseID for the common case were orm ids are integers.

    Particularly when orm ids are selected from a sequence.
    """

    def to_orm(self) -> Ok[int] | InvalidORMIdentifierError:
        if not self._value:
            return InvalidORMIdentifierError("id was empty")
        try:
            return Ok(int(self._value))
        except ValueError:
            return InvalidORMIdentifierError(
                "conversion to orm failed", id_value=self._value
            )

    @classmethod
    def from_orm(cls, orm_id: int | None):
        # Note that "0" is not a valid identifier in this scheme.
        # A feature rather than a bug since 0 is the same as
        # unspecified in protos, and database sequences for
        # generating sequential ids start at 1.
        return cls(str(orm_id or ""))


class BaseIDFromStr(BaseID[str]):
    """Implementation of BaseID for the case were orm ids are strings."""

    def to_orm(self) -> Ok[str] | InvalidORMIdentifierError:
        if not self._value:
            return InvalidORMIdentifierError("id was empty")
        return Ok(self._value)

    @classmethod
    def from_orm(cls, orm_id: str | None):
        return cls(orm_id or "")


class OrgID(BaseIDFromStr):
    """A unique identifier for an organization."""

    @property
    def is_super_user(self):
        return self._value == corvic.context.SUPERUSER_ORG_ID

    @property
    def is_nobody(self):
        return self._value == corvic.context.NOBODY_ORG_ID


class RoomID(BaseIDFromInt):
    """A unique identifier for a room."""


class ResourceID(BaseIDFromInt):
    """A unique identifier for a resource."""


class SourceID(BaseIDFromInt):
    """A unique identifier for a source."""


class FeatureViewID(BaseIDFromInt):
    """A unique identifier for a feature view."""


class FeatureViewSourceID(BaseIDFromInt):
    """A unique identifier for a source in a feature view."""


class SpaceID(BaseIDFromInt):
    """A unique identifier for a space."""


class SpaceRunID(BaseIDFromInt):
    """A unique identifier for a space run."""
