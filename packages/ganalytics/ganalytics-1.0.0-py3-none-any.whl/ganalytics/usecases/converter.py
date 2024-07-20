"""Implementation of the converter module.
This module contains the implementation of the report converter
that converts a report to a table-like structure.
"""
from typing import List, Dict, Any

from src.ganalytics.interfaces.iusecases import IReportConverter
from src.ganalytics.domains.analytics import GoogleAnalyticsReport, TableData
from src.ganalytics.interfaces.ilogger import ILogger
from src.ganalytics.utils.validators import BaseUseCase

from injector import inject


class ReportConverter(IReportConverter, BaseUseCase):

    @inject
    def __init__(self, logger: ILogger):
        """Initialize the report converter"""
        self.logger = logger
        super(BaseUseCase, self).__init__()

    def convert_report(self, report: GoogleAnalyticsReport) -> TableData:
        """Convert a report to a table-like structure"""
        table = TableData(columns=[], data=[])
        # -- extract the columns from the report
        for row in report.rows:
            for dimension in row.dimensions:
                if dimension.dimension not in table.columns:
                    table.columns.append(dimension.dimension)
            for metric in row.metrics:
                if metric.metric not in table.columns:
                    table.columns.append(metric.metric)

        # -- extract the data from the report
        for row in report.rows:
            row_data = {}
            for dimension in row.dimensions:
                row_data[dimension.dimension] = dimension.value
            for metric in row.metrics:
                row_data[metric.metric] = metric.value
            table.add_row(row_data)

        return table


class ReportExporter(BaseUseCase):
    pass