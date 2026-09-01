import pathlib
import sqlite3
import tempfile
from os import PathLike
from uuid import UUID

import requests

from scpytsdk._exceptions import (
    DatabaseExists,
    DatabaseNotFound,
    GroupNotFound,
    InvalidOriginDatabase
)
from scpytsdk.enums import TokenAuthorization
from scpytsdk.models import Database, DatabaseEncryption, DatabaseSeed


def _dump_mem_to_wal(origin: sqlite3.Connection) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = pathlib.Path(tmp) / "tmp.db"

        try:
            dest = sqlite3.connect(db_path)
            dest.execute("PRAGMA journal_mode=WAL")
            origin.backup(dest)
            dest.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        finally:
            dest.close()

        return db_path.read_bytes()


class _db:
    def __init__(self, _endpoint: str, _organization: str, _headers: dict):
        self._endpoint = _endpoint
        self._headers = _headers
        self._organization = _organization

    def __repr__(self):
        """
        Human readable representation of this class.
        """

        return (
            f"{self.__class__.__name__}({self._endpoint=!r}, {self._organization=!r})"
        )

    def list(
        self,
        group_filter: str | None = None,
        schema_filter: str | None = None,
        parent_filter: UUID | Database | None = None,
    ) -> list[Database]:
        """
        Lists all Databases in the organization. Returns a list of Database objects.

        Args:
            group_filter: Allows to filter by group (optional).
            schema_filter: Allows to filter by schema (optional).
            parent_filter: Allows to filter by database parent. Accepts both a database ID and a Database object (optional).

        Returns:
            A list of the dabases as a Database object
        """

        filters = ""

        if group_filter:
            filters += f"?group={group_filter}"

        if schema_filter:
            if filters == "":
                filters += "?"
            else:
                filters += "&"

            filters += f"schema={schema_filter}"

        if parent_filter:
            if filters == "":
                filters += "?"
            else:
                filters += "&"

            if isinstance(parent_filter, Database):
                filters += f"parent={parent_filter.DbId}"
            else:
                filters += f"parent={parent_filter}"

        r = requests.get(
            f"{self._endpoint}/v1/organizations/{self._organization}/databases{filters}",
            headers=self._headers,
        )

        dbs: list[Database] = []

        for db_json in r.json()["databases"]:
            dbs += [Database(**db_json)]

        return dbs

    def delete(self, database: str | Database) -> None:
        """
        Deletes a database in the organization.

        Args:
            database: The database to delete. Accepts either the name of the database or its object.

        Raises:
            DatabaseNotFound: If the database doesn't exist
        """

        if isinstance(database, Database):
            r = requests.delete(
                f"{self._endpoint}/v1/organizations/{self._organization}/databases/{database.Name}",
                headers=self._headers,
            )
        else:
            r = requests.delete(
                f"{self._endpoint}/v1/organizations/{self._organization}/databases/{database}",
                headers=self._headers,
            )

        if r.status_code == 404:
            raise DatabaseNotFound

    def retrieve(self, database: str) -> Database:
        """
        Retrieves information about the specified database.

        Args:
            database: The database to retrieve information from. Accepts only the name of the database

        Returns:
            The database object

        Raises:
            DatabaseNotFound: If the database doesn't exist
        """

        r = requests.get(
            f"{self._endpoint}/v1/organizations/{self._organization}/databases/{database}",
            headers=self._headers,
        )

        if r.status_code == 404:
            raise DatabaseNotFound

        return Database(**r.json()["database"])

    def create(
        self,
        name: str,
        group: str = "default",
        seed: DatabaseSeed | None = None,
        size_limit: str | None = None,
        encryption: DatabaseEncryption | None = None,
    ) -> Database:
        """
        Creates a database and then retrieves information from it.

        Args:
            name: The name of the database to create.
            group: The group where the database will be created. Defaults to "default".
            seed: The database seed. Optional. Used either if the database must be a branch of an existing database or if a libsql database must be uploaded.
            size_limit: The maximum size of the database in bytes. Values with units (such as 1G, 512M, etc.) are also accepted.
            encryption: The remote encryption object (optional).

        Returns:
            The created database as a Database object

        Raises:
            GroupNotFound:  If the group does not exist
            DatabaseExists: If a database with the same name already exists
        """

        body: dict[str, str | dict] = {"name": name, "group": group}

        if seed:
            body["seed"] = seed.__dict__

        if size_limit:
            body["size_limit"] = size_limit

        if encryption:
            body["remote_encryption"] = encryption.__dict__

        r = requests.post(
            f"{self._endpoint}/v1/organizations/{self._organization}/databases",
            headers=self._headers,
            json=body,
        )

        if r.status_code == 400:
            raise GroupNotFound

        if r.status_code == 409:
            raise DatabaseExists

        return self.retrieve(name)

    def create_token(
        self,
        database: Database | str,
        expiration: str | None = None,
        authorization: TokenAuthorization | None = None,
    ):
        """
        Creates a JWT token used for reading, writing and syncing to and from the database.

        Args:
            database: The database that the token will be allowed to access. Can be either the database's name or its object.
            expiration: The expiration time of the token (eg. 2d30m, 1w3d, 2h, etc.). Optional, defaults to "never"
            authorization: The authorization enum for the token. Optional, defaults to FULL_ACCESS

        Returns:
            The created token

        Raises:
            DatabaseNotFound: If the database does not exist
        """

        query: str = ""

        if expiration:
            query += f"?expiration={expiration}"

        if authorization:
            if query != "":
                query += "&"
            else:
                query += "?"
            query += f"authorization={authorization}"

        if isinstance(database, Database):
            r = requests.post(
                f"{self._endpoint}/v1/organizations/{self._organization}/databases/{database.Name}/auth/tokens{query}",
                headers=self._headers,
            )
        else:
            r = requests.post(
                f"{self._endpoint}/v1/organizations/{self._organization}/databases/{database}/auth/tokens{query}",
                headers=self._headers,
            )

        if r.status_code == 404:
            raise DatabaseNotFound

        return r.json()["jwt"]

    def rotate_tokens(self, database: Database | str) -> None:
        """
        Rotate (i.e. invalidate) all tokens for a database.

        Args:
            database: The database for which the keys must be rotated. Can be either its name or its object.

        Raises:
            DatabaseNotFound: If the database does not exist
        """
        if isinstance(database, Database):
            r = requests.post(
                f"{self._endpoint}/v1/organizations/{self._organization}/databases/{database.Name}/auth/rotate",
                headers=self._headers,
            )
        else:
            r = requests.post(
                f"{self._endpoint}/v1/organizations/{self._organization}/databases/{database}/auth/rotate",
                headers=self._headers,
            )

        if r.status_code == 404:
            raise DatabaseNotFound

    def upload(
        self,
        database: Database,
        origin: str | PathLike[str] | sqlite3.Connection,
        encryption: DatabaseEncryption | None = None,
    ) -> None:
        """
        Uploads the origin to a database created with seed type set as SeedType.DATABASE_UPLOAD

        Args:
            database: The Database object of the target database
            origin: The origin database. Can either be a path to a local file or a database dump in memory
            encryption: The origin database encryption object (optional).

        Raises:
            InvalidOriginDatabase: If the origin database is not valid
        """

        if isinstance(origin, (PathLike, str)):
            db = open(origin, "rb").read()
        elif "wal" in origin.execute("PRAGMA journal_mode").fetchall()[0]:
            print("wal")
            db = origin.serialize()
        elif "memory" in origin.execute("PRAGMA journal_mode").fetchall()[0]:
            print("mem")
            db = _dump_mem_to_wal(origin)
        else:
            raise InvalidOriginDatabase

        headers: dict[str, str] = {"Content-length": str(len(db))}

        headers["Authorization"] = f"Bearer {self.create_token(database, '1m')}"

        if encryption:
            headers["x-turso-encryption-key"] = encryption.encryption_key
            headers["x-turso-encryption-cipher"] = encryption.encryption_cipher

        r = requests.post(
            f"https://{database.Hostname}/v1/upload", data=db, headers=headers
        )

        if r.status_code == 400:
            print(r.json())
            raise InvalidOriginDatabase
