from src.ganalytics.domains.analytics import (
    DateRange,
    MetricData,
    DimensionData,
    ReportRow,
    GoogleAnalyticsReport,
)

from src.ganalytics.infrastructure.google_analytics_api import GoogleAnalyticsAPI
from src.ganalytics.infrastructure.logger import Logger
from src.ganalytics.interfaces.ianalytics import (
    IAnalyticsAPI,
)
from src.ganalytics.interfaces.ilogger import ILogger
from src.ganalytics.interfaces.iusecases import (
    IReportUseCase,
    IReportTemplate,
    IReportConverter,
)
from src.ganalytics.usecases.converter import ReportConverter
from src.ganalytics.usecases.pull_reports import PullReport
from src.ganalytics.usecases.report_templates import ReportTemplates
from src.ganalytics.utils.errors import (
    AppError,
    EnvironmentVariableError,
    GoogleAnalyticsAPIError,
    ReportNotFoundError,
    ReportParamsError,
)
from src.ganalytics.utils.validators import (
    BaseValidator,
    BaseUseCase,
    BaseRepository,
    BaseAPI,
)
from src.ganalytics.config import configure
from src.ganalytics.client import ReportClient


__all__ = [
    "DateRange",
    "MetricData",
    "DimensionData",
    "ReportRow",
    "GoogleAnalyticsReport",
    "GoogleAnalyticsAPI",
    "Logger",
    "IAnalyticsAPI",
    "ILogger",
    "IReportUseCase",
    "IReportTemplate",
    "IReportConverter",
    "ReportConverter",
    "PullReport",
    "ReportTemplates",
    "AppError",
    "EnvironmentVariableError",
    "GoogleAnalyticsAPIError",
    "ReportNotFoundError",
    "ReportParamsError",
    "BaseValidator",
    "BaseUseCase",
    "BaseRepository",
    "BaseAPI",
    "configure",
    "ReportClient"
]


__version__ = "0.0.1"

