"""
Base classes for usecases and external services.
It adds abstraction to handle exceptions and errors.
"""
from src.ganalytics.utils.errors import AppError


class BaseValidator:

    def __init__(self):
        self.unique_error_ids = []
        self.errors = []

    def add_error(self, error: AppError):
        # add and error if it is not already in the list
        if error not in self.errors:
            if not error.error_id in self.unique_error_ids:
                self.unique_error_ids.append(error.error_id)
            self.errors.append(error)

    def is_valid(self):
        return not self.errors
    
    def get_errors(self):
        return self.errors
    
    def clear_errors(self):
        self.errors = []

    def extend_errors(self, errors: list):
        for error in errors:
            self.add_error(error)


class BaseUseCase(BaseValidator):
    pass


class BaseRepository(BaseValidator):
    pass


class BaseAPI(BaseValidator):
    pass