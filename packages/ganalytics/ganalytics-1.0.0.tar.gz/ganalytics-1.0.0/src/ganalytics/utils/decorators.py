"""Custom decorators for Google Analytics API."""

def is_template(func):
    """Decorator to mark a method as a report template."""
    func.is_template = True
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper