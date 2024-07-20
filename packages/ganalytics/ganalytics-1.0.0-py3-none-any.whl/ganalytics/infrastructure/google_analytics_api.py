from src.ganalytics.interfaces.ianalytics import (
    IAnalyticsAPI
)
from src.ganalytics.interfaces.ilogger import ILogger
from src.ganalytics.domains.analytics import (
    MetricData,
    DimensionData,
    ReportRow,
    GoogleAnalyticsReport,
)
from src.ganalytics.utils.validators import BaseAPI
from src.ganalytics.utils.errors import (
    EnvironmentVariableError,
    GoogleAnalyticsAPIError,
)

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Metric,
    Dimension,
    RunReportRequest,
    RunRealtimeReportRequest,
    RunPivotReportRequest,
)

import os

from injector import inject


class GoogleAnalyticsAPI(IAnalyticsAPI, BaseAPI):
    """Google Analytics API class"""

    @inject
    def __init__(self, logger: ILogger):
        """Initialize the Google Analytics API"""
        super(BaseAPI, self).__init__()
        self.logger = logger
        self.__post_init__()

    def check_env_vars(self, env_vars: list):
        """Check if required environment variables are set
        """
        for env_var in env_vars:
            if not os.getenv(env_var):
                self.add_error(
                    EnvironmentVariableError(
                        f"Environment variable {env_var} is not set."
                    )
                )
                self.logger.error(f"Environment variable {env_var} is not set.")

    def __post_init__(self):
        """Post initialization method"""
        # -- check if required environment variables are set
        self.check_env_vars([
            'GA_PROPERTY_ID',
            'GOOGLE_APPLICATION_CREDENTIALS',
        ])
        try:
            self.client = BetaAnalyticsDataClient()
        except Exception as e:
            self.add_error(e)
            self.logger.error(e)

    def run_report(self, start_date: str, end_date: str, metrics: list, dimensions: list) -> GoogleAnalyticsReport:
        """Request a report from the Google Analytics API. This report is not in real-time.
        It contains statistics derived from the data collected over a period of time.
        """
        response = None
        try:
            # -- create a request
            request = RunReportRequest(
                property=f"properties/{os.getenv('GA_PROPERTY_ID')}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                metrics=[Metric(name=metric) for metric in metrics],
                dimensions=[Dimension(name=dimension) for dimension in dimensions],
            )
            # -- get the report
            response = self.client.run_report(request)
            response = self._parse_response(response)
        except Exception as e:
            self.add_error(GoogleAnalyticsAPIError(f"Error getting report: {e}"))
            self.logger.error(f"Error getting report: {e}")

        return response
    
    def run_realtime_report(self, metrics: list, dimensions: list) -> GoogleAnalyticsReport:
        """Request a real-time report from the Google Analytics API. This report contains
        real-time statistics about the data collected.
        """
        response = None
        try:
            # -- create a request
            request = RunRealtimeReportRequest(
                property=f"properties/{os.getenv('GA_PROPERTY_ID')}",
                dimensions=[Dimension(name=dimension) for dimension in dimensions],
                metrics=[Metric(name=metric) for metric in metrics],
            )
            # -- get the report
            response = self.client.run_report(request)
            response = self._parse_response(response)
        except Exception as e:
            self.add_error(GoogleAnalyticsAPIError(f"Error getting real-time report: {e}"))
            self.logger.error(f"Error getting real-time report: {e}")

        return response
    
    def _parse_response(self, response) -> GoogleAnalyticsReport:
        """Parse the response from the Google Analytics API.
        """
        report = GoogleAnalyticsReport()
        if response:
            metric_headers = [metric.name for metric in response.metric_headers]
            dimension_headers = [header.name for header in response.dimension_headers]
            metrics = []
            dimensions = []
            for row in response.rows:
                for metric_value, metric_header in zip(row.metric_values, metric_headers):
                    metrics.append(MetricData(metric=metric_header, value=metric_value.value))
                for dimension_value, dimension_header in zip(row.dimension_values, dimension_headers):
                    dimensions.append(DimensionData(dimension=dimension_header, value=dimension_value.value))
                report.add_row(ReportRow(metrics=metrics, dimensions=dimensions))
        return report
