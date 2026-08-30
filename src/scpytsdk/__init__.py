import requests
from scpytsdk.classes import Database
from scpytsdk.exceptions import InvalidApikey, InvalidOrganization, DatabaseNotFound

class SCPYTSDK:
    _endpoint: str = "https://api.turso.tech"
    _apikey: str = ""
    _organization: str = ""
    _headers: dict = {}

    def __init__(self, apikey: str, organization_slug: str, endpoint: str = "https://api.turso.tech"):
        if apikey == "":
            raise InvalidApikey

        if organization_slug == "":
            raise InvalidOrganization

        self._endpoint = endpoint

        r = requests.get(f"{endpoint}/v1/auth/validate", headers={"Authorization": f"Bearer {apikey}"})

        if r.status_code != 200:
            print(r.status_code)
            print(dict(r.json()))
            raise InvalidApikey

        self._apikey = apikey

        if requests.get(f"{endpoint}/v1/organizations/{organization_slug}", headers={"Authorization": f"Bearer {apikey}"}).status_code != 200:
            raise InvalidOrganization
        
        self._organization = organization_slug

        self._headers = {"Authorization": f"Bearer {apikey}"}

    def list_dbs(self, group_filter: str | None = None, schema_filter: str | None = None, parent_filter: str | Database | None = None) -> list[Database]:
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

        r = requests.get(f"{self._endpoint}/v1/organizations/{self._organization}/databases{filters}", headers=self._headers)
        
        json = r.json()

        dbs: list[Database] = []

        for db_json in json["databases"]:
            dbs += [Database(**db_json)]

        return dbs

    def delete_db(self, database: str | Database) -> None:
        r = requests.Response()
        
        if isinstance(database, Database):
            r = requests.delete(f"https://api.turso.tech/v1/organizations/{self._organization}/databases/{database.Name}", headers=self._headers)
        else:
            r = requests.delete(f"https://api.turso.tech/v1/organizations/{self._organization}/databases/{database}", headers=self._headers)

        if r.status_code == 404:
            raise DatabaseNotFound()

        return

    def retreive_db(self, database: str | Database) -> Database:
        r = requests.Response()
        if isinstance(database, Database):
            r = requests.get(f"{self._endpoint}/v1/organizations/{self._organization}/databases/{database.Name}")
        else:
            r = requests.get(f"{self._endpoint}/v1/organizations/{self._organization}/databases/{database.Name}")

        return Database(r.json()["database"])
