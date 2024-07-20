from typing import overload
import abc

import System
import System.Security
import System.Security.Permissions


class SecurityPermissionFlag(System.Enum):
    """Obsoletions.CodeAccessSecurityMessage"""

    ALL_FLAGS = 16383

    ASSERTION = 1

    BINDING_REDIRECTS = 8192

    CONTROL_APP_DOMAIN = 1024

    CONTROL_DOMAIN_POLICY = 256

    CONTROL_EVIDENCE = 32

    CONTROL_POLICY = 64

    CONTROL_PRINCIPAL = 512

    CONTROL_THREAD = 16

    EXECUTION = 8

    INFRASTRUCTURE = 4096

    NO_FLAGS = 0

    REMOTING_CONFIGURATION = 2048

    SERIALIZATION_FORMATTER = 128

    SKIP_VERIFICATION = 4

    UNMANAGED_CODE = 2


class PermissionState(System.Enum):
    """This class has no documentation."""

    NONE = 0

    UNRESTRICTED = 1


class SecurityAction(System.Enum):
    """Obsoletions.CodeAccessSecurityMessage"""

    ASSERT = 3

    DEMAND = 2

    DENY = 4

    INHERITANCE_DEMAND = 7

    LINK_DEMAND = 6

    PERMIT_ONLY = 5

    REQUEST_MINIMUM = 8

    REQUEST_OPTIONAL = 9

    REQUEST_REFUSE = 10


class SecurityAttribute(System.Attribute, metaclass=abc.ABCMeta):
    """Obsoletions.CodeAccessSecurityMessage"""

    @property
    def action(self) -> int:
        """This property contains the int value of a member of the System.Security.Permissions.SecurityAction enum."""
        ...

    @property
    def unrestricted(self) -> bool:
        ...

    def __init__(self, action: System.Security.Permissions.SecurityAction) -> None:
        """This method is protected."""
        ...

    def create_permission(self) -> System.Security.IPermission:
        ...


class CodeAccessSecurityAttribute(System.Security.Permissions.SecurityAttribute, metaclass=abc.ABCMeta):
    """Obsoletions.CodeAccessSecurityMessage"""

    def __init__(self, action: System.Security.Permissions.SecurityAction) -> None:
        """This method is protected."""
        ...


class SecurityPermissionAttribute(System.Security.Permissions.CodeAccessSecurityAttribute):
    """Obsoletions.CodeAccessSecurityMessage"""

    @property
    def assertion(self) -> bool:
        ...

    @property
    def binding_redirects(self) -> bool:
        ...

    @property
    def control_app_domain(self) -> bool:
        ...

    @property
    def control_domain_policy(self) -> bool:
        ...

    @property
    def control_evidence(self) -> bool:
        ...

    @property
    def control_policy(self) -> bool:
        ...

    @property
    def control_principal(self) -> bool:
        ...

    @property
    def control_thread(self) -> bool:
        ...

    @property
    def execution(self) -> bool:
        ...

    @property
    def flags(self) -> int:
        """This property contains the int value of a member of the System.Security.Permissions.SecurityPermissionFlag enum."""
        ...

    @property
    def infrastructure(self) -> bool:
        ...

    @property
    def remoting_configuration(self) -> bool:
        ...

    @property
    def serialization_formatter(self) -> bool:
        ...

    @property
    def skip_verification(self) -> bool:
        ...

    @property
    def unmanaged_code(self) -> bool:
        ...

    def __init__(self, action: System.Security.Permissions.SecurityAction) -> None:
        ...

    def create_permission(self) -> System.Security.IPermission:
        ...


