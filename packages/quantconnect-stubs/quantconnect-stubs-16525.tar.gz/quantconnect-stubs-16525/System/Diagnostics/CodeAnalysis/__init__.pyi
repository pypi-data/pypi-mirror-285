from typing import overload
import System
import System.Diagnostics.CodeAnalysis


class ExcludeFromCodeCoverageAttribute(System.Attribute):
    """This class has no documentation."""

    @property
    def justification(self) -> str:
        """Gets or sets the justification for excluding the member from code coverage."""
        ...

    def __init__(self) -> None:
        ...


class UnscopedRefAttribute(System.Attribute):
    """Used to indicate a byref escapes and is not scoped."""

    def __init__(self) -> None:
        """Initializes a new instance of the UnscopedRefAttribute class."""
        ...


class ExperimentalAttribute(System.Attribute):
    """Indicates that an API is experimental and it may change in the future."""

    @property
    def diagnostic_id(self) -> str:
        """Gets the ID that the compiler will use when reporting a use of the API the attribute applies to."""
        ...

    @property
    def url_format(self) -> str:
        """
        Gets or sets the URL for corresponding documentation.
         The API accepts a format string instead of an actual URL, creating a generic URL that includes the diagnostic ID.
        """
        ...

    def __init__(self, diagnosticId: str) -> None:
        """
        Initializes a new instance of the ExperimentalAttribute class, specifying the ID that the compiler will use
         when reporting a use of the API the attribute applies to.
        
        :param diagnosticId: The ID that the compiler will use when reporting a use of the API the attribute applies to.
        """
        ...


class ConstantExpectedAttribute(System.Attribute):
    """Indicates that the specified method parameter expects a constant."""

    @property
    def min(self) -> System.Object:
        """Indicates the minimum bound of the expected constant, inclusive."""
        ...

    @property
    def max(self) -> System.Object:
        """Indicates the maximum bound of the expected constant, inclusive."""
        ...


class SuppressMessageAttribute(System.Attribute):
    """Suppresses reporting of a specific code analysis rule violation, allowing multiple suppressions on a single code artifact. Does not apply to compiler diagnostics."""

    @property
    def category(self) -> str:
        ...

    @property
    def check_id(self) -> str:
        ...

    @property
    def scope(self) -> str:
        ...

    @property
    def target(self) -> str:
        ...

    @property
    def message_id(self) -> str:
        ...

    @property
    def justification(self) -> str:
        ...

    def __init__(self, category: str, checkId: str) -> None:
        ...


