"""Implementation of the usecases for the analytics module."""
from src.ganalytics.interfaces.iusecases import (
    IReportUseCase,
    IReportTemplate,
)
from src.ganalytics.interfaces.ianalytics import IAnalyticsAPI
from src.ganalytics.interfaces.ilogger import ILogger
from src.ganalytics.utils.validators import (
    BaseUseCase,
)
from src.ganalytics.utils.errors import (
    ReportNotFoundError,
    ReportParamsError,
)
from src.ganalytics.domains.analytics import DateRange

from typing import List

from injector import inject


class PullReport(IReportUseCase, BaseUseCase):

    @inject
    def __init__(self, logger: ILogger, report_template: IReportTemplate, analytics_api: IAnalyticsAPI):
        """Initialize the ReportUseCase class.
        """
        super(BaseUseCase, self).__init__()
        self.analytics_api = analytics_api
        self.report_template = report_template
        self.logger = logger

    def list_reports(self) -> List[str]:
        """List the available reports.
        """
        return self.report_template.list_templates()

    def pull_report(self, report_name: str, date_range: dict):
        """Pull a report snapshot from the Google Analytics API.
        """
        # -- validate the date range
        try:
            date_range = DateRange(**date_range)
        except ValueError as e:
            self.add_error(ReportParamsError(str(e)))
            # log the error
            self.logger.error(str(e))
            return
        
        # -- get the report template
        template = self.report_template.get_template(report_name)
        if not self.report_template.is_valid():
            self.extend_errors(self.report_template.get_errors())
            return  # bail out if there are errors
        
        #  extract the metrics and dimensions from the template
        metrics = template.get('metrics')
        dimensions = template.get('dimensions')
        start_date = date_range.start_date
        end_date = date_range.end_date
        
        # call the analytics api to get the report
        report = self.analytics_api.run_report(
            start_date=start_date.strftime('%Y-%m-%d'),  # convert date to string
            end_date=end_date.strftime('%Y-%m-%d'),  # convert date to string
            metrics=metrics,
            dimensions=dimensions
        )
        if not self.analytics_api.is_valid():
            self.extend_errors(self.analytics_api.get_errors())
            return  # bail out if there are errors

        return report
    
    def pull_realtime_report(self, report_name: str):
        """Pull a realtime report snapshot from the Google Analytics API.
        """
        # -- get the report template
        template = self.report_template.get_template(report_name)
        if not self.report_template.is_valid():
            self.extend_errors(self.report_template.get_errors())
            return
        
        #  extract the metrics and dimensions from the template
        metrics = template.get('metrics')
        dimensions = template.get('dimensions')
        
        # call the analytics api to get the report
        report = self.analytics_api.run_realtime_report(
            metrics=metrics,
            dimensions=dimensions
        )
        if not self.analytics_api.is_valid():
            self.extend_errors(self.analytics_api.get_errors())
            return  # bail out if there are errors

        return report