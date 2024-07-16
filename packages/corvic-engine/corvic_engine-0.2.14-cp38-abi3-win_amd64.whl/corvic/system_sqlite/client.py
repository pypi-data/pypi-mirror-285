"""Sqlite backed system client."""

import contextlib
import dataclasses
import pathlib
import sqlite3
import tempfile
from collections.abc import Iterator
from pathlib import Path

import duckdb
import sqlalchemy as sa

import corvic.context
import corvic.orm
import corvic.system
from corvic.result import NotFoundError
from corvic.system_sqlite.fs_blob_store import FSBlobClient
from corvic.system_sqlite.rdbms_blob_store import RDBMSBlobClient
from corvic.system_sqlite.staging import DuckDBStaging


@contextlib.contextmanager
def _context_requester_org_id_is(value: str | corvic.orm.OrgID) -> Iterator[None]:
    old_requester = corvic.context.requester.get()
    new_requester = corvic.context.Requester(org_id=str(value))
    corvic.context.requester.set(new_requester)
    yield
    corvic.context.requester.set(old_requester)


@contextlib.contextmanager
def _context_requester_org_is_superuser() -> Iterator[None]:
    with _context_requester_org_id_is(corvic.context.SUPERUSER_ORG_ID):
        yield


@sa.event.listens_for(sa.Engine, "connect")
def set_sqlite_pragma(dbapi_connection: sqlite3.Connection | None, _) -> None:
    """Tell sqlite to respect foreign key constraints.

    By default, sqlite doesn't check foreign keys. It can though if you tell it to.
    Postresql always does
    """
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


def _initialize_db_from_empty(engine: sa.Engine):
    """Initialize uninitialized database.

    To setup a real database, use the database migration process. However, the SQL there
    is Postgres-specific. This initialization process is at the ORM level so it will
    work for any compatible backend, assuming no state needs to be migrated.
    """
    with _context_requester_org_is_superuser(), corvic.orm.Session(engine) as session:
        new_org = corvic.orm.Org(name="default_org")
        session.add(new_org)

        session.commit()

        new_room = corvic.orm.Room(name="default_room")
        new_room.org_id = new_org.id
        session.add(new_room)

        session.commit()

        new_org_id = corvic.orm.OrgID.from_orm(new_org.id)
        new_room_id = corvic.orm.RoomID.from_orm(new_room.id)
        new_default_entry = corvic.orm.DefaultObjects(
            default_org=new_org_id.to_orm().unwrap_or_raise(),
            default_room=new_room_id.to_orm().unwrap_or_raise(),
        )
        session.add(new_default_entry)

        session.commit()


def _get_default_org_id(engine: sa.Engine):
    with corvic.orm.Session(engine) as session:
        defaults_row = session.scalars(
            sa.select(corvic.orm.DefaultObjects)
            .order_by(corvic.orm.DefaultObjects.version.desc())
            .limit(1)
        ).one_or_none()
        if not defaults_row:
            raise NotFoundError("defaults table was uninitialized")
        return corvic.orm.OrgID.from_orm(defaults_row.default_org)


class Client(corvic.system.Client):
    """Client for the sqlite system implementation."""

    def __init__(
        self,
        sqlite_file: pathlib.Path,
        vector_column_names_to_sizes: dict[str, int] | None = None,
        *,
        use_sqlite_for_blobs=False,
        keep_blob_state_after_delete=False,
    ):
        sqlite_file_exists = sqlite_file.exists()

        self._sa_engine = sa.create_engine(f"sqlite:///{sqlite_file}")
        if use_sqlite_for_blobs:
            self._blob_client = RDBMSBlobClient(self._sa_engine)
        elif keep_blob_state_after_delete:
            self._blob_client = FSBlobClient(sqlite_file.parent / "corvic_blob_data")
        else:
            self._tempdir = tempfile.TemporaryDirectory()  # cleaned up on client gc
            self._blob_client = FSBlobClient(Path(self._tempdir.name))
        # For convenience of setting up local development, use
        # bucket host that matches default configuration of
        # "-m corvic_test.ingest service upload": localhost:4000
        bucket = self._blob_client.bucket("localhost:4000")
        if not bucket.exists():
            bucket.create()
        self._storage_manager = corvic.system.StorageManager(
            self._blob_client,
            bucket_name=bucket.name,
            unstructured_prefix="unstructured_data",
            tabular_prefix="tabular_data",
            space_run_prefix="experiement_run_data",
            vector_prefix="vectors",
        )
        corvic.orm.Base.metadata.create_all(self._sa_engine)
        duck_db_conn = duckdb.connect(":memory:")
        self._staging_db = DuckDBStaging(
            self._storage_manager,
            duck_db_conn,
            vector_column_names_to_sizes
            or corvic.system.DEFAULT_VECTOR_COLUMN_NAMES_TO_SIZES,
        )
        random_text_embedder = corvic.system.RandomTextEmbedder()
        self._executor = corvic.system.ValidateFirstExecutor(
            corvic.system.InMemoryExecutor(
                self._staging_db, self._storage_manager, random_text_embedder
            )
        )

        if not sqlite_file_exists:
            _initialize_db_from_empty(self._sa_engine)

        # when using the system_sqlite client the caller almost always
        # does not care about org. So set the org premtively to the default
        # org.
        corvic.context.requester.set(
            dataclasses.replace(
                corvic.context.requester.get(),
                org_id=str(_get_default_org_id(self._sa_engine)),
            )
        )
        self._text_embedder = corvic.system.RandomTextEmbedder()

    @property
    def blob_client(self) -> RDBMSBlobClient | FSBlobClient:
        return self._blob_client

    @property
    def storage_manager(self) -> corvic.system.StorageManager:
        return self._storage_manager

    @property
    def sa_engine(self) -> sa.Engine:
        return self._sa_engine

    @property
    def staging_db(self) -> DuckDBStaging:
        return self._staging_db

    @property
    def executor(self) -> corvic.system.OpGraphExecutor:
        return self._executor

    @property
    def text_embedder(self) -> corvic.system.TextEmbedder:
        return self._text_embedder
