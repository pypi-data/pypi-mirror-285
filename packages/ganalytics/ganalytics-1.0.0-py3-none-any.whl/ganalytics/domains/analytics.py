"""Domain module for common analytics operations."""
from .base import DomainBase

from pydantic import field_validator, model_validator, condecimal

from datetime import date
from typing import List, Dict, Any


class DateRange(DomainBase):
    """Date range domain class"""
    start_date: date
    end_date: date

    @model_validator(mode='after')
    def validate_date_range(cls, values):
        """Validate the date range"""
        if values.start_date >= values.end_date:
            raise ValueError('start_date must be less than end_date')
        return values


class MetricData(DomainBase):
    """Metric data domain class"""
    metric: str
    value: str


class DimensionData(DomainBase):
    """Dimension data domain class"""
    dimension: str
    value: str


class ReportRow(DomainBase):
    """Report row domain class"""
    metrics: List[MetricData]
    dimensions: List[DimensionData]


class GoogleAnalyticsReport(DomainBase):
    rows: List[ReportRow] = []

    def add_row(self, row: ReportRow):
        """Add a row to the report"""
        # -- add the row to the report if it doesn't already exist
        if row not in self.rows:
            self.rows.append(row)


class TableData(DomainBase):
    """Domain model to represent table-like structure"""
    columns: List[str]
    data: List[Dict[str, Any]]

    def add_row(self, row: Dict[str, Any]):
        """Add a row to the table"""
        # -- add the row to the table if it doesn't already exist
        if row not in self.data:
            self.data.append(row)

    def filter_data(self, criteria: Dict[str, Any]) -> 'TableData':
        """Filter the data based on the criteria
        Args:
            criteria: A dictionary containing the criteria to filter the data
        Returns: A new TableData object containing the filtered data
        """
        # -- filter the data based on the criteria
        filtered_data = [
            row for row in self.data
            if all(row.get(key) == value for key, value in criteria.items())
        ]
        return TableData(columns=self.columns, data=filtered_data)
    
    def describe(self) -> Dict[str, Any]:
        """
        Provides a summary statistics of the table data.

        Returns:
            dict: A dictionary containing the summary statistics of the table data.
        """
        summary = {
            column: {
                "count": 0,
                "unique": 0,
                "top": None,
                "freq": 0
            } for column in self.columns
        }
        column_values = {column: [] for column in self.columns}

        for row in self.data:
            for column in self.columns:
                column_values[column].append(row.get(column))

        for column, values in column_values.items():
            unique_values = set(values)
            summary[column]["count"] = len(values)
            summary[column]["unique"] = len(unique_values)
            if unique_values:
                summary[column]["top"] = max(unique_values, key=values.count)
                summary[column]["freq"] = values.count(summary[column]["top"])

        return summary
    
    def head(self, n: int = 5) -> 'TableData':
        """
        Returns the first n rows of the table data.

        Args:
            n (int): The number of rows to return.

        Returns:
            TableData: A new TableData object containing the first n rows of the table data.
        """
        return TableData(columns=self.columns, data=self.data[:n])
    
    def tail(self, n: int = 5) -> 'TableData':
        """
        Returns the last n rows of the table data.

        Args:
            n (int): The number of rows to return.

        Returns:
            TableData: A new TableData object containing the last n rows of the table data.
        """
        return TableData(columns=self.columns, data=self.data[-n:])
    
    def __str__(self):
        """Pretty print in tabular format"""
        output = ''
        # -- print the column headers
        output += ' | '.join(self.columns) + '\n'
        output += '-' * (len(self.columns) * 3) + '\n'
        # -- print the data
        for row in self.data:
            output += ' | '.join([str(row.get(col, '')) for col in self.columns]) + '\n'
        return output
