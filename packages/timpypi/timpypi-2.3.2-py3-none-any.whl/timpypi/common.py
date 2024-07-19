

import logging


_logger = logging.getLogger(__name__)
def exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            _logger.error(f"An error occurred in {func.__name__}: {e}")
            return None
    return wrapper