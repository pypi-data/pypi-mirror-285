from typing import overload
import System
import System.Configuration.Assemblies


class AssemblyHashAlgorithm(System.Enum):
    """This class has no documentation."""

    NONE = 0

    MD_5 = ...

    SHA_1 = ...

    SHA_256 = ...

    SHA_384 = ...

    SHA_512 = ...


class AssemblyVersionCompatibility(System.Enum):
    """This class has no documentation."""

    SAME_MACHINE = 1

    SAME_PROCESS = 2

    SAME_DOMAIN = 3


