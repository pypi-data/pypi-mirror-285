"""Exception Module fot T-QA process."""


class TQaBaseException(Exception):
    """Base exception for qa lib."""

    pass


class TQaBaseSilentException(TQaBaseException):
    """Base Exception with no logging messages."""

    pass


class SkipIfItLocalRunException(TQaBaseSilentException):
    """Skip process if it is local run."""

    pass


class SkipIfItWorkItemsNotSetException(TQaBaseException):
    """Skip process if it is local run."""

    pass


class NotLoggedInToGoogleException(TQaBaseSilentException):
    """Exception raise when lib could not log in to google services."""

    pass


class SkipProdRunException(TQaBaseException):
    """Exception to skip the prod run."""

    pass


class TestCaseFileDoesNotExistException(TQaBaseException):
    """Exception to raise when test cases file does not exist."""

    pass


class ServiceAccountKeyPathException(TQaBaseException):
    """Exception raise if lib could not get service account key."""

    pass


class TestCaseReadException(TQaBaseException):
    """Exception raise if lib could not read Yaml file."""

    pass


class AdminCodeException(TQaBaseException):
    """Exception raise if lib could not get Admin code from work items."""

    pass
