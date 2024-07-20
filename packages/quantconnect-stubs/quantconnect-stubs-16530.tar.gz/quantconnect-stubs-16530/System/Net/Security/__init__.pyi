from typing import overload
import System
import System.Net.Security


class SslPolicyErrors(System.Enum):
    """This class has no documentation."""

    NONE = ...

    REMOTE_CERTIFICATE_NOT_AVAILABLE = ...

    REMOTE_CERTIFICATE_NAME_MISMATCH = ...

    REMOTE_CERTIFICATE_CHAIN_ERRORS = ...


class AuthenticationLevel(System.Enum):
    """This class has no documentation."""

    NONE = 0

    MUTUAL_AUTH_REQUESTED = 1

    MUTUAL_AUTH_REQUIRED = 2


