import requests

from scpytsdk._db import _db
from scpytsdk._exceptions import InvalidApikey, InvalidOrganization
from scpytsdk._group import _group


class SCPYTSDK:
    def __init__(
        self,
        apikey: str,
        organization_slug: str,
        endpoint: str = "https://api.turso.tech",
    ):
        """
        Create a SCPYTSDK object that can connect to the Turso Platform API.

        Args:
            apikey: The Turso Platform API Key
            organization_slug: The organization slug of the orgranization you want to access
            endpoint: The endpoint of the API. Defaults to "https://api.turso.tech"

        Raises:
            InvalidApikey: If the key is not valid
            InvalidOrganization: If the organization slug is not valid
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

        self.db = _db(self._endpoint, self._organization, self._headers)
        self.group = _group(self._endpoint, self._organization, self._headers)

    def __repr__(self):
        """
        Human readable representation of this class.
        """

        return (
            f"{self.__class__.__name__}({self._endpoint=!r}, {self._organization=!r})"
        )
