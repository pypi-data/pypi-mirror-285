"""Common machineray for wrapping proto messages."""

from __future__ import annotations

import abc
import copy
from typing import Generic, TypeGuard, TypeVar

import google.protobuf.message

from corvic.op_graph.errors import OpParseError

SomeMessage = TypeVar("SomeMessage", bound=google.protobuf.message.Message)


class ProtoWrapper(Generic[SomeMessage]):
    """Provides common operations for classes that wrap a proto message."""

    _proto: SomeMessage

    def __init__(self, proto: SomeMessage):
        self._proto = proto

    @staticmethod
    def _is_self_type(
        val: object,
    ) -> TypeGuard[ProtoWrapper[google.protobuf.message.Message]]:
        return bool(isinstance(val, ProtoWrapper))

    def __eq__(self, other: object) -> bool:
        """Instances are equal if their underlying messages are equal.

        As a convenience, equality also applies if the target of comparison is a raw
        message.
        """
        if self._is_self_type(other):
            other = other._proto
        return self._proto == other  # pyright: ignore[reportUnknownVariableType]

    def to_proto(self) -> SomeMessage:
        # copy since a caller could modify this and wrappers are immutable
        return copy.copy(self._proto)

    def to_bytes(self):
        return self._proto.SerializeToString()


class ProtoOneofWrapper(ProtoWrapper[SomeMessage], abc.ABC):
    """ProtoWrapper around a specific "oneof" field in SomeMessage."""

    def __init__(self, proto: SomeMessage):
        super().__init__(proto)
        if self.expected_oneof_field() != self._proto.WhichOneof(self.oneof_name()):
            raise OpParseError(
                "expected oneof field not populated",
                expected=self.expected_oneof_field(),
            )

    def __hash__(self) -> int:
        return self._proto.SerializeToString(deterministic=True).__hash__()

    @classmethod
    @abc.abstractmethod
    def oneof_name(cls) -> str:
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def expected_oneof_field(cls) -> str:
        raise NotImplementedError()
