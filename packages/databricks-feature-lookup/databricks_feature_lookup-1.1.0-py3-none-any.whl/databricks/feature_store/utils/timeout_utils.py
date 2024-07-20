import functools
import logging
import os
import signal

TOTAL_REQUEST_TIMEOUT_SECONDS_ENV_VAR = "FEATURE_STORE_TOTAL_REQUEST_TIMEOUT_SECONDS"
# The default total request timeout in lookup client is 90% of the default model serving request timeout
DEFAULT_TOTAL_REQUEST_TIMEOUT_SECONDS = int(0.9 * 120)

_logger = logging.getLogger(__name__)


def get_total_request_timeout_seconds():
    model_request_timeout = os.environ.get(TOTAL_REQUEST_TIMEOUT_SECONDS_ENV_VAR)
    if model_request_timeout:
        try:
            return int(model_request_timeout)
        except ValueError:
            _logger.warning(
                f"Unable to cast {model_request_timeout} to int. Using default timeout."
            )
            return DEFAULT_TOTAL_REQUEST_TIMEOUT_SECONDS
    else:
        return DEFAULT_TOTAL_REQUEST_TIMEOUT_SECONDS


TOTAL_REQUEST_TIMEOUT_SECONDS = get_total_request_timeout_seconds()


def timeout(seconds):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise Exception(
                f"Exceeded maximum wait time of {seconds} seconds to lookup the features"
            )

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            result = func(*args, **kwargs)
            signal.alarm(0)
            return result

        return wrapper

    return decorator
