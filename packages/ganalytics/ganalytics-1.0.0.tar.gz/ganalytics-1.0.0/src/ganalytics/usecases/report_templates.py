"""Report templates for Google Analytics reports.
Note:
    Refer to this link https://calibrate-analytics.com/insights/2023/07/24/The-Top-API-Metric-and-Dimension-Combos-for-Google-Analytics-4/
    for a list of the top API metric and dimension combos for standard Google Analytics 4 reports.
"""
from src.ganalytics.domains.constants import Metric, Dimension, RealtimeMetric, RealtimeDimension
from src.ganalytics.utils.errors import ReportNotFoundError, ReportParamsError
from src.ganalytics.interfaces.ilogger import ILogger
from src.ganalytics.utils.validators import BaseUseCase
from src.ganalytics.utils.decorators import is_template

from src.ganalytics.interfaces.iusecases import IReportTemplate
from src.ganalytics.interfaces.ilogger import ILogger

from typing import List

from injector import inject

import inspect


class ReportTemplates(IReportTemplate, BaseUseCase):
    """Report templates for Google Analytics reports.
    
    Note:
        Only static methods are used to define the report templates. Do not add
        any static methods that are not report templates.
    """

    @inject
    def __init__(self, logger: ILogger):
        """Initialize the ReportTemplates class."""
        super(BaseUseCase, self).__init__()
        self.logger = logger

    @staticmethod
    def traffic_overview(*args, **kwargs) -> dict:
        """
        This report provides an overview of the traffic on the website. It
        includes the number of active users, sessions, etc. The report is
        useful for understanding the general traffic patterns on the website.
        """
        return {
            'metrics': [
                Metric.SESSIONS.value,
                Metric.ENGAGED_SESSIONS.value,
                Metric.AVERAGE_SESSION_DURATION.value,
                Metric.NEW_USERS.value,
                Metric.TOTAL_USERS.value,
            ],
            'dimensions': [
                Dimension.DATE.value,
                Dimension.SESSION_SOURCE.value,
                Dimension.SESSION_CAMPAIGN_ID.value,
                Dimension.DEVICE_CATEGORY.value,
            ],
        }
    
    @staticmethod
    def realtime_traffic_overview() -> dict:
        return {
            'metrics': [
                RealtimeMetric.ACTIVE_USERS.value,
            ],
            'dimensions': [
                RealtimeDimension.CITY.value,
            ]
        }
    
    @staticmethod
    def top_pages() -> dict:
        """
        This report provides data on the most viewed pages on your site.
        """
        return {
            'metrics': [
                Metric.SCREEN_PAGE_VIEWS.value,
                Metric.TOTAL_USERS.value,
                Metric.USER_ENGAGEMENT_DURATION.value,
                Metric.ENGAGED_SESSIONS.value,
                Metric.SESSIONS.value,
            ],
            'dimensions': [
                Dimension.DATE.value,
                Dimension.FULL_PAGE_URL.value,
                Dimension.PLATFORM.value,
            ],
        }
    
    
    @staticmethod
    def geographic_overview() -> dict:
        """
        This report provides an overview of the geographic distribution of
        the website traffic.
        """
        return {
            'metrics': [
                Metric.SESSIONS.value,
                Metric.ENGAGED_SESSIONS.value,
                Metric.TOTAL_USERS.value,
                Metric.NEW_USERS.value,
            ],
            'dimensions': [
                Dimension.COUNTRY.value,
                Dimension.REGION.value,
                Dimension.CITY.value,
                Dimension.DATE.value,
            ],
        }
    
    @staticmethod
    def landing_page_performance() -> dict:
        """
        This report provides data on the performance of the landing pages on
        your site.
        """
        return {
            'metrics': [
                Metric.SESSIONS.value,
                Metric.ENGAGED_SESSIONS.value,
                Metric.TOTAL_USERS.value,
                Metric.NEW_USERS.value,
            ],
            'dimensions': [
                Dimension.DATE.value,
                Dimension.LANDING_PAGE.value,
                Dimension.DEVICE_CATEGORY.value,
                Dimension.SESSION_SOURCE.value,
                Dimension.SESSION_CAMPAIGN_ID.value,
            ],
        }
    
    @staticmethod
    def top_referrers() -> dict:
        """
        This report provides data on the top referrers to your site.
        """
        return {
            'metrics': [
                Metric.SCREEN_PAGE_VIEWS.value
                ],
            'dimensions': [Dimension.PAGE_REFERRER.value],
        }
    
    @staticmethod
    def user_behaviour() -> dict:
        """User behaviour report template."""
        return {
            'metrics': [
                Metric.ENGAGED_SESSIONS.value,
                Metric.SCREEN_PAGE_VIEWS_PER_USER.value,
                Metric.SCREEN_PAGE_VIEWS_PER_SESSION.value,
                Metric.USER_ENGAGEMENT_DURATION.value,
                ],
            'dimensions': [Dimension.PAGE_PATH.value],
        }
    
    @staticmethod
    def user_acquisition() -> dict:
        """User acquisition report template."""
        return {
            'metrics': [
                Metric.NEW_USERS.value,
                Metric.TOTAL_USERS.value,
                Metric.SESSIONS.value,
                Metric.ENGAGED_SESSIONS.value,
                ],
            'dimensions': [
                Dimension.DATE.value,
                Dimension.SESSION_SOURCE.value,
            ],
        }
    
    def get_template(self, report_name: str):
        """This method is used to get the report template by name.

        Args:
            report_name (str): The name of the report template to get.
        Returns:
            dict: The report template
        """
        try:
            return getattr(self, report_name)()
        except AttributeError:
            self.add_error(ReportNotFoundError(f'Report template `{report_name}` not found'))
            self.logger.error(f"Report template `{report_name}` not found")
            return None

    def list_templates(self) -> List[str]:
        """This method is used to list all the available report templates."""
        actual_templates = []
        # static methods correspond to the report templates
        for name, method in inspect.getmembers(self, predicate=inspect.isfunction):  # use is function for static methods, method for instance methods
            actual_templates.append(name)
        return actual_templates
