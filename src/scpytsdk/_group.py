import requests

from scpytsdk._exceptions import GroupNotFound
from scpytsdk.models import Group


class _group:
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

    def list(self) -> list[Group]:
        """
        List all groups in an organization.

        Returns:
            A list of the group object
        """

        r = requests.get(
            f"{self._endpoint}/v1/organizations/{self._organization}/groups",
            headers=self._headers,
        )

        groups: list[Group] = []

        for group_dict in r.json()["groups"]:
            groups.append(Group(**group_dict))

        return groups

    def retrieve(self, group: str) -> Group:
        """
        Retrieves information from a group in the organization.

        Args:
            group: The group's name.

        Returns:
            A group object.

        Raises:
            GroupNotFound: If the group does not exist
        """

        r = requests.get(
            f"{self._endpoint}/v1/organizations/{self._organization}/groups/{group}",
            headers=self._headers,
        )

        if r.status_code == 404:
            raise GroupNotFound

        return Group(**r.json()["group"])

    def delete(self, group: Group | str):
        """
        Deletes a group from the organization.

        Args:
            group: The group to be deleted. Can be either the group's name or its object

        Raises:
            GroupNotFound: If the group does not exist
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
