from typing import Optional
from .data import DataObject, SameMimeType
from .root import AbstractAssociation, View, AbstractDesktopObject, desktop_object_type_for_name
from .volume import AWSFileSystem, DEFAULT_FILE_SYSTEM
from .keychain import Credentials, AWSCredentials
from .person import Person, Group, Role
from abc import ABC, abstractmethod
from collections.abc import Sequence
from email_validator import validate_email, EmailNotValidError  # Leave this here for other modules to use
from functools import partial


class Account(DataObject, ABC):
    """
    Abstract base class for user accounts.
    """
    def __init__(self):
        super().__init__()
        self.__file_system_type: str | None = None
        self.__file_system_name: str | None = DEFAULT_FILE_SYSTEM
        self.__credential_type_name: str | None = None

    @property
    def file_system_type(self) -> str | None:
        """The type of file system used for storage of REST resources that are accessed using this account."""
        return self.__file_system_type

    @file_system_type.setter
    def file_system_type(self, file_system_type: str | None):
        self.__file_system_type = str(file_system_type) if file_system_type is not None else None

    @property
    def file_system_name(self) -> str | None:
        """The name of the file system used for storage of REST resources that are accessed using this account."""
        return self.__file_system_name

    @file_system_name.setter
    def file_system_name(self, file_system_name: str | None):
        self.__file_system_name = str(file_system_name) if file_system_name is not None else None

    @abstractmethod
    def get_role_to_assume(self, user: Person, groups: Sequence[Group]) -> str | None:
        """
        Finds and returns a role to assume from the provided groups. The user must be a member of these groups. This
        method assumes that the account subclass has attributes that allow selecting a role from those in the provided
        groups.

        :param user: the person.
        :param groups: the groups to select from.
        :return: a role, or None if no suitable role was found.
        """
        pass

    @abstractmethod
    def new_credentials(self, person: Person, groups: Sequence[Group] | None = None) -> Credentials:
        """
        Returns a new Credentials object, populated from the attributes of this account object.
        Implementations of this method should set any assumed role using this object's
        get_role_to_assume method. It may also set default values for any of the Credential object's
        attributes. At minimum, it will set default values for its display_name and name attributes.

        :param person: the person.
        :param groups: optional groups to select from when setting an assumed role.
        :return: a Credentials object.
        """
        pass


class AWSAccount(Account, SameMimeType):
    """
    Represents an AWS account in the HEA desktop. Contains functions that allow access and setting of the value. Below are the attributes that can be accessed.

    account_id (str)              : 1234567890
    account_name (str)            : HCI - name
    full_name (str)               : john smith
    phone_number (str)            : 123-456-7890
    alternate_contact_name (str)  : bob smith
    alternate_email_address (str) : 123@hciutah.edu
    alternate_phone_number (str)  : 123-456-7890
    """
    def __init__(self) -> None:
        super().__init__()
        self.__full_name: Optional[str] = None
        self.__phone_number: Optional[str] = None
        self.__alternate_contact_name: Optional[str] = None
        self.__alternate_email_address: Optional[str] = None
        self.__alternate_phone_number: Optional[str] = None
        self.__email_address: Optional[str] = None
        self.file_system_type = AWSFileSystem.get_type_name()
        self.credential_type_name = AWSCredentials.get_type_name()

    @classmethod
    def get_mime_type(cls) -> str:
        """
        Returns the mime type for AWSAccount objects.

        :return: application/x.awsaccount
        """
        return 'application/x.awsaccount'

    @property
    def mime_type(self) -> str:
        """Read-only. The mime type for AWSAccount objects, application/x.awsaccount."""
        return type(self).get_mime_type()


    @property
    def full_name(self) -> Optional[str]:
        """Returns the full name of person associated with this account"""
        return self.__full_name

    @full_name.setter
    def full_name(self, full_name: Optional[str]) -> None:
        """Sets the full name of person associated with this account"""
        self.__full_name = str(full_name) if full_name is not None else None

    @property
    def phone_number(self) -> Optional[str]:
        """Returns the phone number associated with the account"""
        return self.__phone_number

    @phone_number.setter
    def phone_number(self, phone_number: Optional[str]) -> None:
        """Sets the phone number associated with the account"""
        self.__phone_number = str(phone_number) if phone_number is not None else None

    @property
    def alternate_contact_name(self) -> Optional[str]:
        """Returns the alternate contact full name of person associated with this account"""
        return self.__alternate_contact_name

    @alternate_contact_name.setter
    def alternate_contact_name(self, alternate_contact_name: Optional[str]) -> None:
        """Sets the alternate contact full name of person associated with this account"""
        self.__alternate_contact_name = str(alternate_contact_name) if alternate_contact_name is not None else None

    @property
    def alternate_email_address(self) -> Optional[str]:
        """Returns the alternate contact e-mail address associated with the account"""
        return self.__alternate_email_address

    @alternate_email_address.setter
    def alternate_email_address(self, alternate_email_address: Optional[str]) -> None:
        """Sets the alternate contact e-mail address associated with the account"""
        self.__alternate_email_address = _validate_email(str(alternate_email_address)).email \
            if alternate_email_address is not None else None

    @property
    def alternate_phone_number(self) -> Optional[str]:
        """Returns the alternate contact phone number associated with the account"""
        return self.__alternate_phone_number

    @alternate_phone_number.setter
    def alternate_phone_number(self, alternate_phone_number: Optional[str]) -> None:
        """Sets the alternate contact phone number associated with the account"""
        self.__alternate_phone_number = str(alternate_phone_number) if alternate_phone_number is not None else None

    @property
    def email_address(self) -> Optional[str]:
        return self.__email_address

    @email_address.setter
    def email_address(self, email_address: Optional[str]) -> None:
        """Sets the email address associated with the account"""
        self.__email_address = _validate_email(str(email_address)).email if email_address is not None else None

    @property
    def type_display_name(self) -> str:
        return 'AWS Account'

    def get_role_to_assume(self, user: Person, groups: Sequence[Group]) -> str | None:
        for group in groups:
            role = next(filter(lambda role: role.find(self.id) > -1,
                               (Role.id_to_role(role_id) for role_id in group.role_ids)), None)
            if role is not None and user.group_ids.count(group.id) > 0:
                return role
        return None

    def new_credentials(self, person: Person, groups: Sequence[Group] | None = None) -> AWSCredentials:
        credentials = AWSCredentials()
        if groups is not None:
            credentials.role = self.get_role_to_assume(person, groups)
        if credentials.role is None:
            raise ValueError('AWS Credentials must have a non-None role attribute')
        credentials.name = f'{person.id}_{self.type}_{self.id}'
        credentials.display_name = f'{self.display_name} - {person.display_name}'
        return credentials


class AccountView(AbstractDesktopObject, View):
    def __init__(self):
        super().__init__()
        self.__id: str | None = None
        self.__actual_object_id: str | None = None
        self.__actual_object_type_name: str | None = None
        self.__type_display_name: str | None = None
        self.__file_system_type: str | None = None
        self.__file_system_name: str | None = None

    @property
    def id(self) -> str | None:
        return self.__id

    @id.setter
    def id(self, id_: str | None):
        self.__id = str(id_) if id_ is not None else None

    @property
    def actual_object_id(self) -> str | None:
        return self.__actual_object_id

    @actual_object_id.setter
    def actual_object_id(self, actual_object_id: str | None):
        self.__actual_object_id = str(actual_object_id) if actual_object_id is not None else None
        self.id = f'{self.actual_object_type_name}^{self.__actual_object_id}'

    @property
    def actual_object_type_name(self) -> str | None:
        return self.__actual_object_type_name

    @actual_object_type_name.setter
    def actual_object_type_name(self, actual_object_type_name: str | None):
        self.__actual_object_type_name = str(actual_object_type_name) if actual_object_type_name is not None else None
        self.id = f'{self.__actual_object_type_name}^{self.actual_object_id}'

    @property
    def type_display_name(self) -> str:
        if self.__type_display_name is not None:
            return self.__type_display_name
        if (actual := self.actual_object_type_name) is not None:
            return desktop_object_type_for_name(actual).__name__
        else:
            return 'Account'

    @type_display_name.setter
    def type_display_name(self, type_display_name: str):
        self.__type_display_name = str(type_display_name) if type_display_name is not None else None

    @property
    def file_system_type(self):
        """The type of file system used for storage of REST resources that are accessed using this account."""
        return self.__file_system_type

    @file_system_type.setter
    def file_system_type(self, file_system_type):
        self.__file_system_type = str(file_system_type) if file_system_type is not None else None

    @property
    def file_system_name(self):
        """The name of the file system used for storage of REST resources that are accessed using this account."""
        return self.__file_system_name

    @file_system_name.setter
    def file_system_name(self, file_system_name):
        self.__file_system_name = str(file_system_name) if file_system_name is not None else None


class AccountAssociation(AbstractAssociation):
    @property
    def allowed_actual_object_type_names(self) -> list[str]:
        return [Account.get_type_name(), AWSAccount.get_type_name()]


_validate_email = partial(validate_email, check_deliverability=False)
