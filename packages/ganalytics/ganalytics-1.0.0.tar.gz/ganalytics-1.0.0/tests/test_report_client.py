import unittest
import os

from src.ganalytics.client import ReportClient
from src.ganalytics.domains.analytics import (
    GoogleAnalyticsReport,
    TableData
)


class ReportClientTestCase(unittest.TestCase):
    """Test case for the report client"""

    def setUp(self):
        # setup environment variables
        os.environ['GA_PROPERTY_ID'] = '450165182'
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'tests/secrets/google-analytics-key.json'
        # get the report usecase
        self.client = ReportClient()

    def test_pull_report_snapshot(self):
        """Test the report client."""
        self.assertIsNotNone(self.client)

        report = self.client.pull_report_snapshot(
            report_name='traffic_overview',
            date_range={
                'start_date': '2024-07-01',
                'end_date': '2024-07-20'
            }
        )

        self.assertIsNotNone(report)
        self.assertIsInstance(report, GoogleAnalyticsReport)

    def test_convert_report(self):
        """Test the report converter."""
        report = self.client.pull_report_snapshot(
            report_name='geographic_overview',
            date_range={
                'start_date': '2024-07-01',
                'end_date': '2024-07-19'
            }
        )

        table = self.client.convert_report(report)
        self.assertIsNotNone(table)
        self.assertIsInstance(table, TableData)

    def test_list_reports(self):
        """Test the list reports method."""
        reports = self.client.list_reports()
        self.assertIsNotNone(reports)
        self.assertIsInstance(reports, list)
        self.assertTrue(len(reports) > 0)
        print(reports)

if __name__ == "__main__":
    unittest.main()