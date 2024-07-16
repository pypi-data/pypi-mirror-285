from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class BlobUrlList(_message.Message):
    __slots__ = ("blob_urls",)
    BLOB_URLS_FIELD_NUMBER: _ClassVar[int]
    blob_urls: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, blob_urls: _Optional[_Iterable[str]] = ...) -> None: ...

class EmbeddingMetrics(_message.Message):
    __slots__ = ("ne_sum", "condition_number", "rcondition_number", "stable_rank")
    NE_SUM_FIELD_NUMBER: _ClassVar[int]
    CONDITION_NUMBER_FIELD_NUMBER: _ClassVar[int]
    RCONDITION_NUMBER_FIELD_NUMBER: _ClassVar[int]
    STABLE_RANK_FIELD_NUMBER: _ClassVar[int]
    ne_sum: float
    condition_number: float
    rcondition_number: float
    stable_rank: float
    def __init__(self, ne_sum: _Optional[float] = ..., condition_number: _Optional[float] = ..., rcondition_number: _Optional[float] = ..., stable_rank: _Optional[float] = ...) -> None: ...
