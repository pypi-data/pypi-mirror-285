"""Type aliases used across corvic."""

import os
from collections.abc import Iterable, Mapping
from typing import Any, Literal, TypeAlias

PathLike: TypeAlias = str | bytes | os.PathLike[Any]

JSONExpressable = (
    bool
    | int
    | str
    | float
    | None
    | Iterable["JSONExpressable"]
    | Mapping[str, "JSONExpressable"]
)

VectorSimilarityMetric: TypeAlias = Literal["cosine", "euclidean"]

__all__ = [
    "JSONExpressable",
    "PathLike",
    "VectorSimilarityMetric",
]
