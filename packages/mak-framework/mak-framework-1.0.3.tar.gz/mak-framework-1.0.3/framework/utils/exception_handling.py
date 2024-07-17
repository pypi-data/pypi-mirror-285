import pytest
import functools
from playwright.sync_api import TimeoutError, Error
from framework.utils.utils import LoggerUtils

logger = LoggerUtils()


def handle_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TimeoutError as te:
            logger.log_error(f"TimeoutError occurred: {te}")
            pytest.fail(f"TimeoutError occurred: {te}")
        except Error as e:
            logger.log_error(f"Playwright Error occurred: {e}")
            pytest.fail(f"Playwright Error occurred: {e}")
        except AssertionError as ae:
            logger.log_error(f"AssertionError occurred: {ae}")
            pytest.fail(f"AssertionError occurred: {ae}")
        except (RuntimeError, ValueError) as critical_ex:
            logger.log_error(f"Critical exception occurred: {critical_ex}")
            pytest.fail(f"Critical exception occurred: {critical_ex}")
        except Exception as ex:
            logger.log_error(f"An unexpected error occurred: {ex}")
            pytest.fail(f"An unexpected error occurred: {ex}")

    return wrapper
