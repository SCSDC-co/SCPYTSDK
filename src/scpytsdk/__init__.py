import requests
from uuid import UUID
from time import sleep
from typing import Any
from scpytsdk.classes import Database, DatabaseSeed
from scpytsdk.exceptions import (
    InvalidApikey,
    InvalidOrganization,
    DatabaseNotFound,
    GroupNotFound,
    DatabaseExists,
)


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
            print(r.status_code)
            print(dict(r.json()))
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

        json = r.json()

        dbs: list[Database] = []

        for db_json in json["databases"]:
            dbs += [Database(**db_json)]

        return dbs

    def delete_db(self, database: str | Database) -> None:
        r = requests.Response()

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

        return

    def retreive_db(self, database: str | Database) -> Database:
        r = requests.Response()

        if isinstance(database, Database):
            r = requests.get(
                f"{self._endpoint}/v1/organizations/{self._organization}/databases/{database.Name}",
                headers=self._headers,
            )
        else:
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
    ) -> Database:
        body: dict[str, Any] = {"name": name, "group": group}

        if seed:
            body["seed"] = seed.__dict__

        if size_limit:
            body["size_limit"] = size_limit

        r = requests.post(
            f"{self._endpoint}/v1/organizations/{self._organization}/databases",
            headers=self._headers,
            json=body,
        )

        if r.status_code == 400:
            raise GroupNotFound

        if r.status_code == 409:
            raise DatabaseExists

        sleep(0.5)

        return self.retreive_db(name)

    def create_db_token(self, database: Database | str) -> str:
        r = requests.Response()

        if isinstance(database, Database):
            r = requests.post(
                f"{self._endpoint}/v1/organizations/{self._organization}/databases/{database.Name}/auth/tokens",
                headers=self._headers,
            )
        else:
            r = requests.post(
                f"{self._endpoint}/v1/organizations/{self._organization}/databases/{database}/auth/tokens",
                headers=self._headers,
            )

        if r.status_code == 404:
            raise DatabaseNotFound

        return r.json()["jwt"]

    def rotate_db_tokens(self, database: Database | str) -> None:
        r = requests.Response()

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

        return None
