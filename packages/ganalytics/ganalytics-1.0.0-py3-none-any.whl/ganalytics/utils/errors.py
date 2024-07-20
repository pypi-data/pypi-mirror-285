"""Custom errors for the ganalytics module."""
import uuid


class AppError(Exception):
    """
    Base class for exceptions in this module.
    """

    def __init__(self, message:str, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        # generate a unique id for the error
        self.error_id = uuid.uuid4().hex
        self.message = message


class EnvironmentVariableError(AppError):
    """
    Exception raised for errors related to environment variables.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message:str, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.message = message


class GoogleAnalyticsAPIError(AppError):
    """
    Exception raised for errors related to the Google Analytics API.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message:str, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.message = message


class ReportNotFoundError(AppError):
    """
    Exception raised when a report is not found.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message:str, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.message = message


class ReportParamsError(AppError):
    """
    Exception raised when report parameters are missing.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message:str, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.message = message