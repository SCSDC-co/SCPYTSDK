import pathlib
import sqlite3
import tempfile
from os import PathLike
from uuid import UUID

import requests

from scpytsdk.classes import Database, DatabaseEncryption, DatabaseSeed, Group
from scpytsdk.enums import TokenAuthorization
from scpytsdk.exceptions import (
    DatabaseExists,
    DatabaseNotFound,
    GroupNotFound,
    InvalidApikey,
    InvalidOrganization,
    InvalidOriginDatabase,
)


def dump_mem_to_wal(origin: sqlite3.Connection) -> bytes:
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


class SCPYTSDK:
    _endpoint: str = "https://api.turso.tech"
    _apikey: str = ""
    _organization: str = ""
    _headers: dict = {}

    def __init__(
        self,
        apikey: str,
        organization_slug: str,
        endpoint: str = "https://api.turso.tech",
    ):
        """
        Create a SCPYTSDK object that can connect to the Turso Platform API.
        apikey: The Turso Platform API Key
        organization_slug: The organization slug of the orgranization you want to access
        endpoint: The endpoint of the API. Defaults to "https://api.turso.tech"
        """
        if apikey == "":
            raise InvalidApikey

        if organization_slug == "":
            raise InvalidOrganization

        self._endpoint = endpoint

        r = requests.get(
            f"{endpoint}/v1/auth/validate",
            headers={
                "Authorization": f"Bearer {apikey}",
                "Content-type": "application/json",
            },
        )

        if r.status_code != 200:
            raise InvalidApikey

        self._apikey = apikey

        if (
            requests.get(
                f"{endpoint}/v1/organizations/{organization_slug}",
                headers={"Authorization": f"Bearer {apikey}"},
            ).status_code
            != 200
        ):
            raise InvalidOrganization

        self._organization = organization_slug

        self._headers = {"Authorization": f"Bearer {apikey}"}

    def list_dbs(
        self,
        group_filter: str | None = None,
        schema_filter: str | None = None,
        parent_filter: UUID | Database | None = None,
    ) -> list[Database]:
        """
        Lists all Databases in the organization. Returns a list of Database objects.
        group_filter: Optional. Allows to filter by group.
        schema_filter: Optional. Allows to filter by schema.
        parent_filter: Optional. Allows to filter by database parent. Accepts both a database ID and a Database object.
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

    def delete_db(self, database: str | Database) -> None:
        """
        Deletes a database in the organization.
        database: The database to delete. Accepts either the name of the database or its object.
        """
        if isinstance(database, Database):
            r = requests.delete(
                f"https://api.turso.tech/v1/organizations/{self._organization}/databases/{database.Name}",
                headers=self._headers,
            )
        else:
            r = requests.delete(
                f"https://api.turso.tech/v1/organizations/{self._organization}/databases/{database}",
                headers=self._headers,
            )

        if r.status_code == 404:
            raise DatabaseNotFound()

    def retrieve_db(self, database: str) -> Database:
        """
        retrieves information about the specified database. Returns the specified database's Database object.
        database: The database to retrieve information from. Accepts ONLY the name of the database
        """
        r = requests.get(
            f"{self._endpoint}/v1/organizations/{self._organization}/databases/{database}",
            headers=self._headers,
        )

        if r.status_code == 404:
            raise DatabaseNotFound

        return Database(**r.json()["database"])

    def create_db(
        self,
        name: str,
        group: str = "default",
        seed: DatabaseSeed | None = None,
        size_limit: str | None = None,
        encryption: DatabaseEncryption | None = None,
    ) -> Database:
        """
        Creates a database and then retrieves information from it. Returns the database's Database object.
        name: The name of the database to create.
        group: The group where the database will be created. Defaults to "default".
        seed: The database seed. Optional. Used either if the database must be a branch of an existing database or if a libsql database must be uploaded.
        size_limit: The maximum size of the database in bytes. Values with units (such as 1G, 512M, etc.) are also accepted.
        encryption: Optional. The remote encryption object.
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

        return self.retrieve_db(name)

    def upload_db(
        self,
        database: Database,
        origin: str | PathLike[str] | sqlite3.Connection,
        encryption: DatabaseEncryption | None = None,
    ) -> None:
        """
        Uploads the origin to a database created with seed type set as SeedType.DATABASE_UPLOAD
        database: The Database object of the target database
        origin: The origin database. Can either be a path to a local file or a database dump in memory
        encryption: Optional. The origin database encryption object.
        """

        if isinstance(origin, (PathLike, str)):
            db = open(origin, "rb").read()
        elif "wal" in origin.execute("PRAGMA journal_mode").fetchall()[0]:
            print("wal")
            db = origin.serialize()
        elif "memory" in origin.execute("PRAGMA journal_mode").fetchall()[0]:
            print("mem")
            db = dump_mem_to_wal(origin)
        else:
            raise InvalidOriginDatabase

        headers: dict[str, str] = {"Content-length": str(len(db))}

        headers["Authorization"] = f"Bearer {self.create_db_token(database, '1m')}"

        if encryption:
            headers["x-turso-encryption-key"] = encryption.encryption_key
            headers["x-turso-encryption-cipher"] = encryption.encryption_cipher

        r = requests.post(
            f"https://{database.Hostname}/v1/upload", data=db, headers=headers
        )

        if r.status_code == 400:
            print(r.json())
            raise InvalidOriginDatabase

    def create_db_token(
        self,
        database: Database | str,
        expiration: str | None = None,
        authorization: TokenAuthorization | None = None,
    ):
        """
        Creates a JWT token used for reading, writing and syncing to and from the database. Returns the token.
        database: The database that the token will be allowed to access. Can be either the database's name or its object.
        expiration: Optional. The expiration time of the token (eg. 2d30m, 1w3d, 2h, etc.). Defaults to "never"
        authorization: Optional. The authorization enum for the token. Defaults to FULL_ACCESS
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

    def rotate_db_tokens(self, database: Database | str) -> None:
        """
        Rotate (i.e. invalidate) all tokens for a database.
        database: The database for which the keys must be rotated. Can be either its name or its object.
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

    def list_groups(self) -> list[Group]:
        """
        List all groups in an organization. Returns a list of Group objects.
        """
        r = requests.get(
            f"{self._endpoint}/v1/organizations/{self._organization}/groups",
            headers=self._headers,
        )

        groups: list[Group] = []

        for group_dict in r.json()["groups"]:
            groups.append(Group(**group_dict))

        return groups

    def retrieve_group(self, group: str) -> Group:
        """
        retrieves information from a group in the organization. Returns a Group object.
        group: The group's name.
        """
        r = requests.get(
            f"{self._endpoint}/v1/organizations/{self._organization}/groups/{group}",
            headers=self._headers,
        )

        if r.status_code == 404:
            raise GroupNotFound

        return Group(**r.json()["group"])

    def delete_group(self, group: Group | str):
        """
        Deletes a group from the organization.
        group: The group to be deleted. Can be either the group's name or its object
        """
        if isinstance(group, Group):
            r = requests.delete(
                f"{self._endpoint}/v1/organizations/{self._organization}/groups/{group.name}",
                headers=self._headers,
            )
        else:
            r = requests.delete(
                f"{self._endpoint}/v1/organizations/{self._organization}/groups/{group}",
                headers=self._headers,
            )

        if r.status_code == 404:
            raise GroupNotFound
