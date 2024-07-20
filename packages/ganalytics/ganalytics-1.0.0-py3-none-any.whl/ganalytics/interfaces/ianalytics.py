from abc import ABCMeta, abstractmethod


class IAnalyticsAPI(metaclass=ABCMeta):
    """Interface for the Analytics API"""
        
    @abstractmethod
    def run_report(self, start_date: str, end_date: str, metrics: list, dimensions: list) -> dict:
        """Get report from the Analytics API
        """
        raise NotImplementedError
    
    @abstractmethod
    def run_realtime_report(self, metrics: list, dimensions: list) -> dict:
        """Get real-time report from the Analytics API
        """
        raise NotImplementedError