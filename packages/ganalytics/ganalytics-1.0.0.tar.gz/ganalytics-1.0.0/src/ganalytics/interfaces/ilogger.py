from abc import ABCMeta, abstractmethod


class ILogger(metaclass=ABCMeta):
    """Logger Interface"""

    @abstractmethod
    def info(self, *args, **kwargs):
        """Log a message"""
        raise NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def error(self, *args, **kwargs):
        """Log an error"""
        raise NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def warning(self, *args, **kwargs):
        """Log a warning"""
        raise NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def debug(self, *args, **kwargs):
        """Log a debug message"""
        raise NotImplementedError("Subclasses must implement this method")