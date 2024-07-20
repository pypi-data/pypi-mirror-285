
import unittest

from src.ganalytics.interfaces.iusecases import IReportUseCase
from src.ganalytics.domains.constants import Metric, Dimension

from tests.config import configure

import os

injector = configure()


class TopReferrersReportTestCase(unittest.TestCase):
    """Test case for the landing page performance report."""

    def setUp(self):
        # setup environment variables
        os.environ['GA_PROPERTY_ID'] = '450165182'
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'tests/secrets/google-analytics-key.json'
        # get the report usecase
        self.report_usecase = injector.get(IReportUseCase)

    def test_top_referrers(self):
        # pull the top referrers report
        report = self.report_usecase.pull_report(
            report_name='top_referrers',
            date_range={
                'start_date': '2024-07-01',
                'end_date': '2024-07-18'
            }
        )
        self.assertTrue(self.report_usecase.is_valid())
        self.assertIsNotNone(report)

    def test_top_referrers_with_invalid_date_range(self):
        # pull the top referrers report with invalid date range
        report = self.report_usecase.pull_report(
            report_name='top_referrers',
            date_range={
                'start_date': '2024-07-18',
                'end_date': '2024-07-01'
            }
        )
        self.assertFalse(self.report_usecase.is_valid())
        self.assertIsNone(report)

    def test_top_referrers_with_invalid_report_name(self):
        # pull the top referrers report with invalid report name
        report = self.report_usecase.pull_report(
            report_name='invalid_report_name',
            date_range={
                'start_date': '2024-07-01',
                'end_date': '2024-07-18'
            }
        )
        self.assertFalse(self.report_usecase.is_valid())
        self.assertIsNone(report)


if __name__ == "__main__":
    unittest.main()