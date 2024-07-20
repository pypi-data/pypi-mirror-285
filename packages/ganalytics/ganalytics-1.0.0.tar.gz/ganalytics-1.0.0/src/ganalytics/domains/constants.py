"""
Metrics and Dimensions Enum for Google Analytics API

Note:
    https://ga-dev-tools.google/ga4/dimensions-metrics-explorer/
    The link above provides a list of all the metrics and dimensions available in the Google Analytics API.
"""

from enum import Enum


class Metric(Enum):
    """Metric Enum for Google Analytics API

    Reference: https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema#metrics
    """
    ACTIVE_1DAY_USERS = 'active1DayUsers'
    ACTIVE_7DAY_USERS = 'active7DayUsers'
    ACTIVE_28DAY_USERS = 'active28DayUsers'
    ACTIVE_USERS = 'activeUsers'
    BOUNCE_RATE = 'bounceRate'
    ENGAGED_SESSIONS = 'engagedSessions'
    ENGAGEMENT_RATE = 'engagementRate'
    NEW_USERS = 'newUsers'
    SCREEN_PAGE_VIEWS = 'screenPageViews'
    SCREEN_PAGE_VIEWS_PER_SESSION = 'screenPageViewsPerSession'
    SCREEN_PAGE_VIEWS_PER_USER = 'screenPageViewsPerUser'
    SCROLLED_USERS = 'scrolledUsers'
    SESSIONS = 'sessions'
    SESSIONS_PER_USER = 'sessionsPerUser'
    USER_ENGAGEMENT_DURATION = 'userEngagementDuration'
    AVERAGE_SESSION_DURATION = 'averageSessionDuration'
    TOTAL_USERS = 'totalUsers'


class Dimension(Enum):
    """Dimension Enum for Google Analytics API
    
    Reference: https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema#dimensions
    """
    CITY = 'city'
    COUNTRY = 'country'
    REGION = 'region'
    DEVICE_CATEGORY = 'deviceCategory'
    DEVICE_MODEL = 'deviceModel'
    MOBILE_DEVICE_MODEL = 'mobileDeviceModel'
    DAY = 'day'
    DAY_OF_WEEK = 'dayOfWeek'
    FULL_PAGE_URL = 'fullPageURL'
    PAGE_LOCATION = 'pageLocation'
    PAGE_PATH = 'pagePath'
    PAGE_PATH_PLUS_QUERY = 'pagePathPlusQueryString'
    PAGE_REFERRER = 'pageReferrer'
    PAGE_TITLE = 'pageTitle'
    PLATFORM = 'platform'
    SEARCH_TERM = 'searchTerm'
    MANUAL_SOURCE = 'manualSource'
    MANUAL_SOURCE_MEDIUM = 'manualSourceMedium'
    OPERATING_SYSTEM = 'operatingSystem'
    OPERATING_SYSTEM_VERSION = 'operatingSystemVersion'
    PERCENT_SCROLLED = 'percentScrolled'
    DATE = 'date'
    SESSION_SOURCE = 'sessionSource'
    SESSION_CAMPAIGN_ID = 'sessionCampaignId'
    LANDING_PAGE = 'landingPage'


class RealtimeMetric(Enum):
    """Realtime Metric Enum for Google Analytics API
    This enum contains the metrics that are available for the realtime report.

    Note:
        Refer to this link for more information: https://developers.google.com/analytics/devguides/reporting/data/v1/realtime-api-schema
    """
    ACTIVE_USERS = 'activeUsers'
    CONVERSIONS = 'conversions'
    EVENT_COUNT = 'eventCount'
    SCREEN_PAGE_VIEWS = 'screenPageViews'


class RealtimeDimension(Enum):
    """Realtime Dimension Enum for Google Analytics API
    This enum contains the dimensions that are available for the realtime report.
    """
    CITY = 'city'
    CITY_ID = 'cityId'
    COUNTRY = 'country'
    COUNTRY_ID = 'countryId'
    DEVICE_CATEGORY = 'deviceCategory'
    MINUTES_AGO = 'minutesAgo'  # The number of minutes ago that the data was collected. 00 - 59
    PLATFORM = 'platform'
    STREAM_ID = 'streamId'
    STREAM_NAME = 'streamName'
    UNIFIED_SCREEN_NAME = 'unifiedScreenName'