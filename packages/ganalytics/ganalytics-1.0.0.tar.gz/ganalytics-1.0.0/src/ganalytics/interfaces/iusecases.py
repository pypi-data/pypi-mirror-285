from abc import ABCMeta, abstractmethod


class IReportUseCase(metaclass=ABCMeta):
    """Interface for the report use case. This interface defines the methods
    that the report use case should implement.
    """

    @abstractmethod
    def pull_report(self, report_name: str, date_range: dict):
        """Pull a report from the Google Analytics API.
        """
        raise NotImplementedError
    
    @abstractmethod
    def pull_realtime_report(self, report_name: str):
        """Pull a real-time report from the Google Analytics API.
        """
        raise NotImplementedError


class IReportTemplate(metaclass=ABCMeta):
    """Interface for the report template. This interface defines the methods
    that the report template should implement.
    """

    @abstractmethod
    def get_template(self, report_name: str):
        """Get the report template by name.
        """
        raise NotImplementedError


class IReportConverter(metaclass=ABCMeta):
    """Interface for the report converter. This interface defines the methods
    that the report converter should implement.
    """

    @abstractmethod
    def convert_report(self, *args, **kwargs):
        """Convert a report to a table-like structure.
        """
        raise NotImplementedError
    