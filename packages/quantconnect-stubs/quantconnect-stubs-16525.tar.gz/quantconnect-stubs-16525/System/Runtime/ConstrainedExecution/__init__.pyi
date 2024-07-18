from typing import overload
import abc

import System
import System.Runtime.ConstrainedExecution


class Consistency(System.Enum):
    """Obsoletions.ConstrainedExecutionRegionMessage"""

    MAY_CORRUPT_PROCESS = 0

    MAY_CORRUPT_APP_DOMAIN = 1

    MAY_CORRUPT_INSTANCE = 2

    WILL_NOT_CORRUPT_STATE = 3


class Cer(System.Enum):
    """Obsoletions.ConstrainedExecutionRegionMessage"""

    NONE = 0

    MAY_FAIL = 1

    SUCCESS = 2


class ReliabilityContractAttribute(System.Attribute):
    """
    Defines a contract for reliability between the author of some code, and the developers who have a dependency on that code.
    
    Obsoletions.ConstrainedExecutionRegionMessage
    """

    @property
    def consistency_guarantee(self) -> int:
        """This property contains the int value of a member of the System.Runtime.ConstrainedExecution.Consistency enum."""
        ...

    @property
    def cer(self) -> int:
        """This property contains the int value of a member of the System.Runtime.ConstrainedExecution.Cer enum."""
        ...

    def __init__(self, consistencyGuarantee: System.Runtime.ConstrainedExecution.Consistency, cer: System.Runtime.ConstrainedExecution.Cer) -> None:
        ...


class PrePrepareMethodAttribute(System.Attribute):
    """Obsoletions.ConstrainedExecutionRegionMessage"""

    def __init__(self) -> None:
        ...


class CriticalFinalizerObject(System.Object, metaclass=abc.ABCMeta):
    """Ensures that all finalization code in derived classes is marked as critical."""

    def __init__(self) -> None:
        """This method is protected."""
        ...


