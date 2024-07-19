from typing import overload
import abc
import typing
import warnings

import System
import System.Collections
import System.Reflection
import System.Runtime.Serialization
import System.Security
import System.Security.Permissions


class SecurityElement(System.Object):
    """This class has no documentation."""

    @property
    def tag(self) -> str:
        ...

    @property
    def attributes(self) -> System.Collections.Hashtable:
        ...

    @property
    def text(self) -> str:
        ...

    @property
    def children(self) -> System.Collections.ArrayList:
        ...

    @overload
    def __init__(self, tag: str) -> None:
        ...

    @overload
    def __init__(self, tag: str, text: str) -> None:
        ...

    def add_attribute(self, name: str, value: str) -> None:
        ...

    def add_child(self, child: System.Security.SecurityElement) -> None:
        ...

    def attribute(self, name: str) -> str:
        ...

    def copy(self) -> System.Security.SecurityElement:
        ...

    def equal(self, other: System.Security.SecurityElement) -> bool:
        ...

    @staticmethod
    def escape(str: str) -> str:
        ...

    @staticmethod
    def from_string(xml: str) -> System.Security.SecurityElement:
        ...

    @staticmethod
    def is_valid_attribute_name(name: str) -> bool:
        ...

    @staticmethod
    def is_valid_attribute_value(value: str) -> bool:
        ...

    @staticmethod
    def is_valid_tag(tag: str) -> bool:
        ...

    @staticmethod
    def is_valid_text(text: str) -> bool:
        ...

    def search_for_child_by_tag(self, tag: str) -> System.Security.SecurityElement:
        ...

    def search_for_text_of_tag(self, tag: str) -> str:
        ...

    def to_string(self) -> str:
        ...


class ISecurityEncodable(metaclass=abc.ABCMeta):
    """This class has no documentation."""

    def from_xml(self, e: System.Security.SecurityElement) -> None:
        ...

    def to_xml(self) -> System.Security.SecurityElement:
        ...


class IStackWalk(metaclass=abc.ABCMeta):
    """This class has no documentation."""

    def Assert(self) -> None:
        ...

    def demand(self) -> None:
        ...

    def deny(self) -> None:
        ...

    def permit_only(self) -> None:
        ...


class IPermission(System.Security.ISecurityEncodable, metaclass=abc.ABCMeta):
    """Obsoletions.CodeAccessSecurityMessage"""

    def copy(self) -> System.Security.IPermission:
        ...

    def demand(self) -> None:
        ...

    def intersect(self, target: System.Security.IPermission) -> System.Security.IPermission:
        ...

    def is_subset_of(self, target: System.Security.IPermission) -> bool:
        ...

    def union(self, target: System.Security.IPermission) -> System.Security.IPermission:
        ...


class PermissionSet(System.Object, System.Collections.ICollection, System.Runtime.Serialization.IDeserializationCallback, System.Security.ISecurityEncodable, System.Security.IStackWalk):
    """This class has no documentation."""

    @property
    def count(self) -> int:
        ...

    @property
    def is_read_only(self) -> bool:
        ...

    @property
    def is_synchronized(self) -> bool:
        ...

    @property
    def sync_root(self) -> System.Object:
        ...

    @overload
    def __init__(self, state: System.Security.Permissions.PermissionState) -> None:
        ...

    @overload
    def __init__(self, permSet: System.Security.PermissionSet) -> None:
        ...

    def add_permission(self, perm: System.Security.IPermission) -> System.Security.IPermission:
        ...

    def add_permission_impl(self, perm: System.Security.IPermission) -> System.Security.IPermission:
        """This method is protected."""
        ...

    def Assert(self) -> None:
        ...

    def contains_non_code_access_permissions(self) -> bool:
        ...

    @staticmethod
    def convert_permission_set(in_format: str, in_data: typing.List[int], out_format: str) -> typing.List[int]:
        """This member is marked as obsolete."""
        warnings.warn("This member is marked as obsolete.", DeprecationWarning)

    def copy(self) -> System.Security.PermissionSet:
        ...

    def copy_to(self, array: System.Array, index: int) -> None:
        ...

    def demand(self) -> None:
        ...

    def deny(self) -> None:
        """This member is marked as obsolete."""
        warnings.warn("This member is marked as obsolete.", DeprecationWarning)

    def equals(self, o: typing.Any) -> bool:
        ...

    def from_xml(self, et: System.Security.SecurityElement) -> None:
        ...

    def get_enumerator(self) -> System.Collections.IEnumerator:
        ...

    def get_enumerator_impl(self) -> System.Collections.IEnumerator:
        """This method is protected."""
        ...

    def get_hash_code(self) -> int:
        ...

    def get_permission(self, perm_class: typing.Type) -> System.Security.IPermission:
        ...

    def get_permission_impl(self, perm_class: typing.Type) -> System.Security.IPermission:
        """This method is protected."""
        ...

    def intersect(self, other: System.Security.PermissionSet) -> System.Security.PermissionSet:
        ...

    def is_empty(self) -> bool:
        ...

    def is_subset_of(self, target: System.Security.PermissionSet) -> bool:
        ...

    def is_unrestricted(self) -> bool:
        ...

    def permit_only(self) -> None:
        ...

    def remove_permission(self, perm_class: typing.Type) -> System.Security.IPermission:
        ...

    def remove_permission_impl(self, perm_class: typing.Type) -> System.Security.IPermission:
        """This method is protected."""
        ...

    @staticmethod
    def revert_assert() -> None:
        ...

    def set_permission(self, perm: System.Security.IPermission) -> System.Security.IPermission:
        ...

    def set_permission_impl(self, perm: System.Security.IPermission) -> System.Security.IPermission:
        """This method is protected."""
        ...

    def to_string(self) -> str:
        ...

    def to_xml(self) -> System.Security.SecurityElement:
        ...

    def union(self, other: System.Security.PermissionSet) -> System.Security.PermissionSet:
        ...


class SecurityException(System.SystemException):
    """This class has no documentation."""

    @property
    def demanded(self) -> System.Object:
        ...

    @property
    def deny_set_instance(self) -> System.Object:
        ...

    @property
    def failed_assembly_info(self) -> System.Reflection.AssemblyName:
        ...

    @property
    def granted_set(self) -> str:
        ...

    @property
    def method(self) -> System.Reflection.MethodInfo:
        ...

    @property
    def permission_state(self) -> str:
        ...

    @property
    def permission_type(self) -> typing.Type:
        ...

    @property
    def permit_only_set_instance(self) -> System.Object:
        ...

    @property
    def refused_set(self) -> str:
        ...

    @property
    def url(self) -> str:
        ...

    @overload
    def __init__(self) -> None:
        ...

    @overload
    def __init__(self, message: str) -> None:
        ...

    @overload
    def __init__(self, message: str, inner: System.Exception) -> None:
        ...

    @overload
    def __init__(self, message: str, type: typing.Type) -> None:
        ...

    @overload
    def __init__(self, message: str, type: typing.Type, state: str) -> None:
        ...

    @overload
    def __init__(self, info: System.Runtime.Serialization.SerializationInfo, context: System.Runtime.Serialization.StreamingContext) -> None:
        """
        This method is protected.
        
        Obsoletions.LegacyFormatterImplMessage
        """
        ...

    def get_object_data(self, info: System.Runtime.Serialization.SerializationInfo, context: System.Runtime.Serialization.StreamingContext) -> None:
        """Obsoletions.LegacyFormatterImplMessage"""
        warnings.warn("Obsoletions.LegacyFormatterImplMessage", DeprecationWarning)

    def to_string(self) -> str:
        ...


class SecurityTreatAsSafeAttribute(System.Attribute):
    """SecurityTreatAsSafe is only used for .NET 2.0 transparency compatibility. Use the SecuritySafeCriticalAttribute instead."""

    def __init__(self) -> None:
        ...


class VerificationException(System.SystemException):
    """This class has no documentation."""

    @overload
    def __init__(self) -> None:
        ...

    @overload
    def __init__(self, message: str) -> None:
        ...

    @overload
    def __init__(self, message: str, innerException: System.Exception) -> None:
        ...

    @overload
    def __init__(self, info: System.Runtime.Serialization.SerializationInfo, context: System.Runtime.Serialization.StreamingContext) -> None:
        """
        This method is protected.
        
        Obsoletions.LegacyFormatterImplMessage
        """
        ...


class SecurityCriticalScope(System.Enum):
    """SecurityCriticalScope is only used for .NET 2.0 transparency compatibility."""

    EXPLICIT = 0

    EVERYTHING = ...


class SecurityCriticalAttribute(System.Attribute):
    """This class has no documentation."""

    @property
    def scope(self) -> int:
        """
        This property contains the int value of a member of the System.Security.SecurityCriticalScope enum.
        
        SecurityCriticalScope is only used for .NET 2.0 transparency compatibility.
        """
        warnings.warn("SecurityCriticalScope is only used for .NET 2.0 transparency compatibility.", DeprecationWarning)

    @overload
    def __init__(self) -> None:
        ...

    @overload
    def __init__(self, scope: System.Security.SecurityCriticalScope) -> None:
        ...


class SecurityRuleSet(System.Enum):
    """This class has no documentation."""

    NONE = 0

    LEVEL_1 = 1

    LEVEL_2 = 2


class SecuritySafeCriticalAttribute(System.Attribute):
    """This class has no documentation."""

    def __init__(self) -> None:
        ...


class SecureString(System.Object, System.IDisposable):
    """This class has no documentation."""

    @property
    def length(self) -> int:
        ...

    @overload
    def __init__(self) -> None:
        ...

    @overload
    def __init__(self, value: typing.Any, length: int) -> None:
        ...

    def append_char(self, c: str) -> None:
        ...

    def clear(self) -> None:
        ...

    def copy(self) -> System.Security.SecureString:
        ...

    def dispose(self) -> None:
        ...

    def insert_at(self, index: int, c: str) -> None:
        ...

    def is_read_only(self) -> bool:
        ...

    def make_read_only(self) -> None:
        ...

    def remove_at(self, index: int) -> None:
        ...

    def set_at(self, index: int, c: str) -> None:
        ...


class SuppressUnmanagedCodeSecurityAttribute(System.Attribute):
    """This class has no documentation."""

    def __init__(self) -> None:
        ...


class SecurityRulesAttribute(System.Attribute):
    """This class has no documentation."""

    @property
    def skip_verification_in_full_trust(self) -> bool:
        ...

    @property
    def rule_set(self) -> int:
        """This property contains the int value of a member of the System.Security.SecurityRuleSet enum."""
        ...

    def __init__(self, ruleSet: System.Security.SecurityRuleSet) -> None:
        ...


class UnverifiableCodeAttribute(System.Attribute):
    """This class has no documentation."""

    def __init__(self) -> None:
        ...


class PartialTrustVisibilityLevel(System.Enum):
    """This class has no documentation."""

    VISIBLE_TO_ALL_HOSTS = 0

    NOT_VISIBLE_BY_DEFAULT = 1


class SecurityTransparentAttribute(System.Attribute):
    """This class has no documentation."""

    def __init__(self) -> None:
        ...


class AllowPartiallyTrustedCallersAttribute(System.Attribute):
    """This class has no documentation."""

    @property
    def partial_trust_visibility_level(self) -> int:
        """This property contains the int value of a member of the System.Security.PartialTrustVisibilityLevel enum."""
        ...

    def __init__(self) -> None:
        ...


