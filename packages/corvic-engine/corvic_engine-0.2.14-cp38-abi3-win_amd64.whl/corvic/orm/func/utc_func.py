"""Defines a sqlalchemy function for utcnow instead of sqlalchemy.func.now()."""

from datetime import timedelta
from typing import Any

from sqlalchemy import sql
from sqlalchemy.ext.compiler import (
    compiles,  # pyright: ignore[reportUnknownVariableType]
)
from sqlalchemy.types import DateTime


class UTCNow(sql.expression.FunctionElement[Any]):
    """Adds a utcnow() expression based on backend db used.

    Implementation follows from documentation from sqlalchemy source at
    sqlalchemy/ext/compiler.py. An offset can be added to support server-side
    offsets from utc now.
    """

    type = DateTime(timezone=True)
    inherit_cache = True

    def __init__(self, offset: timedelta | None = None):
        self.offset = offset or timedelta()

    @property
    def time_offset_clauses(self) -> dict[str, int]:
        return {"days": self.offset.days, "seconds": self.offset.seconds}

    @property
    def has_time_offset(self) -> bool:
        return any(self.time_offset_clauses.values())


@compiles(UTCNow, "postgresql")
def pg_utcnow(
    element: sql.expression.FunctionElement[Any],
    compiler: sql.compiler.SQLCompiler,
    **kw: Any,
):
    """Compile utc timestamp for postgres."""
    match element:
        case UTCNow() as utc_now_elem:
            if utc_now_elem.has_time_offset:
                days = utc_now_elem.offset.days
                seconds = utc_now_elem.offset.seconds
                interval = f"{days} days {seconds} seconds"
                return f"TIMEZONE('utc', CURRENT_TIMESTAMP + '{interval}'::interval)"
            return "TIMEZONE('utc', CURRENT_TIMESTAMP)"

        case _:
            raise TypeError("unexpected type")


@compiles(UTCNow)
def default_sql_utcnow(
    element: sql.expression.FunctionElement[Any],
    compiler: sql.compiler.SQLCompiler,
    **kw: Any,
):
    """Compile utc timestamp for other databases."""
    # this matches sqlalchemy.func.now() and is valid for postgresql
    match element:
        case UTCNow() as utc_now_elem:
            if utc_now_elem.has_time_offset:
                raise RuntimeError("timestamp offsets not supported for this backend")
            return "CURRENT_TIMESTAMP"
        case _:
            raise TypeError("unexpected type")


@compiles(UTCNow, "sqlite")
def sqlite_sql_utcnow(
    element: sql.expression.FunctionElement[Any],
    compiler: sql.compiler.SQLCompiler,
    **kw: Any,
):
    """Compile utc timestamp for sqlite."""
    # default now() visitor for sqlite simply returns 'CURRENT_TIMESTAMP'
    # instead we can use STRFTIME with utcnow format
    match element:
        case UTCNow() as utc_now_elem:
            time_offset_clauses = utc_now_elem.time_offset_clauses
            args = ",".join(
                [
                    "'NOW'",
                    *[
                        f"'{value} {granularity}'"
                        for granularity, value in time_offset_clauses.items()
                        if value
                    ],
                ]
            )
            return rf"(STRFTIME('%Y-%m-%d %H:%M:%f',{args}))"
        case _:
            raise TypeError("unexpected type")
