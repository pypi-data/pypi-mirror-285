import sys
from typing import TypedDict

if sys.version_info >= (3, 10):
    from types import UnionType
else:
    UnionType = type

# Attribute dictionary specifications used by Listener.
class StartSuiteAttributes(TypedDict):
    """Attributes passed to listener v2 ``start_suite`` method.

    See the User Guide for more information.
    """
    id: str
    longname: str
    doc: str
    metadata: 'dict[str, str]'
    source: str
    suites: 'list[str]'
    tests: 'list[str]'
    totaltests: int
    starttime: str

class EndSuiteAttributes(StartSuiteAttributes):
    """Attributes passed to listener v2 ``end_suite`` method.

    See the User Guide for more information.
    """
    endtime: str
    elapsedtime: int
    status: str
    statistics: str
    message: str

class StartTestAttributes(TypedDict):
    """Attributes passed to listener v2 ``start_test`` method.

    See the User Guide for more information.
    """
    id: str
    longname: str
    originalname: str
    doc: str
    tags: 'list[str]'
    template: str
    source: str
    lineno: int
    starttime: str

class EndTestAttributes(StartTestAttributes):
    """Attributes passed to listener v2 ``end_test`` method.

    See the User Guide for more information.
    """
    endtime: str
    elapsedtime: int
    status: str
    message: str

class OptionalKeywordAttributes(TypedDict, total=False):
    """Extra attributes passed to listener v2 ``start/end_keyword`` methods.

    These attributes are included with control structures. For example, with
    IF structures attributes include ``condition``.
    """
    # FOR / ITERATION with FOR
    variables: 'list[str] | dict[str, str]'
    flavor: str
    values: 'list[str]'    # Also RETURN
    # WHILE and IF
    condition: str
    # WHILE
    limit: str
    # EXCEPT
    patterns: 'list[str]'
    pattern_type: str
    variable: str

class StartKeywordAttributes(OptionalKeywordAttributes):
    """Attributes passed to listener v2 ``start_keyword`` method.

    See the User Guide for more information.
    """
    type: str
    kwname: str
    libname: str
    doc: str
    args: 'list[str]'
    assign: 'list[str]'
    tags: 'list[str]'
    source: str
    lineno: int
    status: str
    starttime: str

class EndKeywordAttributes(StartKeywordAttributes):
    """Attributes passed to listener v2 ``end_keyword`` method.

    See the User Guide for more information.
    """
    endtime: str
    elapsedtime: int

class MessageAttributes(TypedDict):
    """Attributes passed to listener v2 ``log_message`` and ``messages`` methods.

    See the User Guide for more information.
    """
    message: str
    level: str
    timestamp: str
    html: str

class LibraryAttributes(TypedDict):
    """Attributes passed to listener v2 ``library_import`` method.

    See the User Guide for more information.
    """
    args: 'list[str]'
    originalname: str
    source: str
    importer: 'str | None'

class ResourceAttributes(TypedDict):
    """Attributes passed to listener v2 ``resource_import`` method.

    See the User Guide for more information.
    """
    source: str
    importer: 'str | None'

class VariablesAttributes(TypedDict):
    """Attributes passed to listener v2 ``variables_import`` method.

    See the User Guide for more information.
    """
    args: 'list[str]'
    source: str
    importer: 'str | None'