import logging

from .root import Permission, PermissionContext
from .data import DataObject, SameMimeType
from typing import Optional, Callable
from enum import Enum

permission_id_dict = {
    'admin_ids': [Permission.COOWNER],
    'manager_ids': [Permission.VIEWER, Permission.EDITOR, Permission.SHARER],
    'member_ids': [Permission.VIEWER, Permission.SHARER]
}


class OrganizationGroup(Enum):
    MEMBER = 10
    MANAGER = 20
    ADMIN = 30


class Organization(DataObject, SameMimeType):
    """
    Represents a directory in the HEA desktop.

    NOTE: THE admin_group_ids, manager_group_ids, and member_group_ids are deprecated and will be removed in a future
    release.
    """

    def __init__(self) -> None:
        super().__init__()
        # id is a super field
        self.__account_ids: set[str] = set()
        self.__principal_investigator_id: Optional[str] = None  # this would be a people id
        self.__admin_ids: list[str] = []  # list of user ids to be admins
        self.__manager_ids: list[str] = []  # list of user ids to be managers
        self.__member_ids: list[str] = []  # list of user ids to be members
        # super's name and display name would be used as org name(required)
        self.__admin_group_ids: list[str] = []
        self.__manager_group_ids: list[str] = []
        self.__member_group_ids: list[str] = []

    @classmethod
    def get_mime_type(cls) -> str:
        """
        Returns the mime type of instances of the Organization class.

        :return: application/x.organization
        """
        return 'application/x.organization'

    @property
    def mime_type(self) -> str:
        """Read-only. The mime type for Organization objects, application/x.organization."""
        return type(self).get_mime_type()

    @property
    def account_ids(self) -> list[str]:
        """The list of accounts owned by this organization."""
        return list(self.__account_ids)

    @account_ids.setter
    def account_ids(self, account_ids: list[str]):
        self.__account_ids.clear()
        if account_ids:
            self.__account_ids.update(str(account_id) for account_id in account_ids)

    def add_account_id(self, account_id: str):
        self.__account_ids.add(str(account_id))

    def remove_account_id(self, account_id: str):
        self.__account_ids.remove(str(account_id))

    @property
    def principal_investigator_id(self) -> Optional[str]:
        """
        The principal investigator person ID. The id cannot be the empty string.
        """
        return self.__principal_investigator_id

    @principal_investigator_id.setter
    def principal_investigator_id(self, principal_investigator_id: Optional[str]) -> None:
        self._raise_if_empty_string(principal_investigator_id)
        self.__principal_investigator_id = str(principal_investigator_id) \
            if principal_investigator_id is not None else None

    @property
    def admin_ids(self) -> list[str]:
        """
        The organization manager ids.
        """
        return [i for i in self.__admin_ids] if self.__admin_ids else []

    @admin_ids.setter
    def admin_ids(self, admin_ids: list[str]) -> None:
        if admin_ids is None:
            self.__admin_ids = []
        elif not isinstance(admin_ids, str):
            self.__admin_ids = [self._raise_if_empty_string(str(i)) for i in admin_ids]
        else:
            self._raise_if_empty_string(admin_ids)
            self.__admin_ids = [str(admin_ids)]

    def add_admin_id(self, admin_id: str) -> None:
        if admin_id == '':
            raise ValueError('admin_id cannot be the empty string')
        self.__admin_ids.append(str(admin_id))

    def remove_admin_id(self, value: str) -> None:
        """
        Removes a REST manager id from the list of ids that are served by this organization. Ignores None values.
        :param value:  str representing the manager id.
        """
        self.__admin_ids.remove(str(value))

    @property
    def manager_ids(self) -> list[str]:
        """
        The organization manager ids.
        """
        return [i for i in self.__manager_ids] if self.__manager_ids else []

    @manager_ids.setter
    def manager_ids(self, manager_ids: list[str]) -> None:
        if manager_ids is None:
            self.__manager_ids = []
        elif not isinstance(manager_ids, str):
            self.__manager_ids = [self._raise_if_empty_string(str(i)) for i in manager_ids]
        else:
            self._raise_if_empty_string(manager_ids)
            self.__manager_ids = [str(manager_ids)]

    def add_manager_id(self, manager_id: str) -> None:
        if manager_id == '':
            raise ValueError('manager_id cannot be the empty string')
        self.__manager_ids.append(str(manager_id))

    def remove_manager_id(self, value: str) -> None:
        """
        Removes a REST manager id from the list of ids that are served by this organization. Ignores None values.
        :param value:  str representing the manager id.
        """
        self.__manager_ids.remove(str(value))

    @property
    def member_ids(self) -> list[str]:
        """
        The organization member ids.
        """
        return [i for i in self.__member_ids]

    @member_ids.setter
    def member_ids(self, member_ids: list[str]) -> None:
        if member_ids is None:
            self.__member_ids = []
        elif not isinstance(member_ids, str):
            self.__member_ids = [self._raise_if_empty_string(str(i)) for i in member_ids]
        else:
            self._raise_if_empty_string(member_ids)
            self.__member_ids = [str(member_ids)]

    def add_member_id(self, member_id: str) -> None:
        if member_id == '':
            raise ValueError('member_id cannot be the empty string')
        self.__member_ids.append(str(member_id))

    def remove_member_id(self, value: str) -> None:
        """
        Removes a REST member id from the list of member ids that are served by this organization. Ignores None values.
        :param value: a str representing the member id.
        """
        self.__member_ids.remove(str(value))

    def dynamic_permission(self, sub: str) -> list[Permission]:
        """
        Returns permissions if the sub is in the member_ids list, or an empty list if not.

        :param sub: the user id (required).
        :return: A list containing Permissions or the empty list.
        """
        try:
            perms: set[Permission] = set()
            if sub == self.principal_investigator_id:
                perms.update(permission_id_dict['manager_ids'])
            for p_id in permission_id_dict:
                if sub in getattr(self, p_id):
                    perms.update(permission_id_dict[p_id])
            return list(perms)
        except:
            logging.exception('Permissions are not correctly configured...returning empty permissions set')
            return []

    @property
    def member_group_ids(self) -> list[str]:
        """
        The Keycloak groups this organization's members are part of.
        """
        return list(self.__member_group_ids)

    @member_group_ids.setter
    def member_group_ids(self, member_group_ids: list[str]):
        if member_group_ids is None:
            self.__member_group_ids = []
        elif not isinstance(member_group_ids, str):
            self.__member_group_ids = [str(i) for i in member_group_ids]
        else:
            self.__member_group_ids = [str(member_group_ids)]

    def add_member_group_id(self, value: str) -> None:
        """
        Adds a group that this organization's members are part of.

        :param value: the group to add.
        """
        self.__member_group_ids.append(str(value))

    def remove_member_group_id(self, value: str) -> None:
        """
        Removes a group that this organization's members are part of.

        :param value: a str representing the member id.
        """
        self.__member_group_ids.remove(str(value))

    @property
    def manager_group_ids(self) -> list[str]:
        """
        The Keycloak groups this organization's managers are part of.
        """
        return list(self.__manager_group_ids)

    @manager_group_ids.setter
    def manager_group_ids(self, manager_group_ids: list[str]):
        if manager_group_ids is None:
            self.__manager_group_ids = []
        elif not isinstance(manager_group_ids, str):
            self.__manager_group_ids = [str(i) for i in manager_group_ids]
        else:
            self.__manager_group_ids = [str(manager_group_ids)]

    def add_manager_group_id(self, value: str) -> None:
        """
        Adds a group that this organization's managers are part of.

        :param value: the group to add.
        """
        self.__manager_group_ids.append(str(value))

    def remove_manager_group_id(self, value: str) -> None:
        """
        Removes a group that this organization's managers are part of.

        :param value: the group to remove.
        """
        self.__manager_group_ids.remove(str(value))

    @property
    def admin_group_ids(self) -> list[str]:
        """
        The Keycloak groups this organization's admins are part of.
        """
        return list(self.__admin_group_ids)

    @admin_group_ids.setter
    def admin_group_ids(self, admin_group_ids: list[str]):
        if admin_group_ids is None:
            self.__admin_group_ids = []
        elif not isinstance(admin_group_ids, str):
            self.__admin_group_ids = [str(i) for i in admin_group_ids]
        else:
            self.__admin_group_ids = [str(admin_group_ids)]

    def add_admin_group_id(self, value: str) -> None:
        """
        Adds a group that this organization's admins are part of.

        :param value: the group to add.
        """
        self.__admin_group_ids.append(str(value))

    def remove_admin_group_id(self, value: str) -> None:
        """
        Removes a group that this organization's admins are part of.

        :param value: the group to remove.
        """
        self.__admin_group_ids.remove(str(value))

    def get_groups(self, sub: str) -> list[str]:
        """
        Gets the groups that the provided user is a part of. This attribute is deprecated.

        :param sub: the user id.
        :return: a list of groups.
        """
        groups: set[str] = set()
        if sub in self.member_ids:
            groups.update(self.member_group_ids)
        if sub in self.manager_group_ids or sub == self.principal_investigator_id:
            groups.update(self.manager_group_ids)
        if sub in self.admin_group_ids:
            groups.update(self.admin_group_ids)
        return list(groups)

    @property
    def type_display_name(self) -> str:
        return "Organization"

    async def get_attribute_permissions(self, attr: str, context: PermissionContext) -> list[Permission]:
        """
        The admin_ids, admin_group_ids, manager_group_ids, and member_group_ids attributes are editable if the user has
        COOWNER permissions. The manager_ids, member_ids, and principal_investigator_id fields are editable if the user
        has COOWNER or EDITOR permissions. Other permissions are set by the superclass' implementation of this method.

        :param sub: the user to check.
        :param attr: the attribute to check.
        :return: the permissions for the attribute.
        """
        def check_perms(perms_checker: Callable[[], bool]) -> list[Permission]:
            if perms_checker():
                return [Permission.VIEWER, Permission.EDITOR]
            else:
                return [Permission.VIEWER]

        if attr in ('admin_ids', 'admin_group_ids', 'manager_group_ids', 'member_group_ids'):
            perms = await self.get_permissions(context)
            return check_perms(lambda: Permission.COOWNER in perms)
        elif attr in ('manager_ids', 'member_ids', 'principal_investigator_id'):
            perms = await self.get_permissions(context)
            return check_perms(lambda: Permission.COOWNER in perms or Permission.EDITOR in perms)
        return await super().get_attribute_permissions(attr, context)

    @staticmethod
    def _raise_if_empty_string(the_string: str | None) -> str | None:
        if the_string == '':
            raise ValueError('cannot be the empty string')
        else:
            return the_string
