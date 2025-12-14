import functools
import json
import logging

import httpx

from config.celeryapp import app

from .access import (
    import_porz_plans_from_sharepoint,
    rewrite_latest_orderbook_from_and_to_sharepoint,
)


log = logging.getLogger("django.sharepoint")


# Retry on these errors, json decode error is included to catch invalid json responses
CONNECTION_ERRORS = (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError)


def connection_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except httpx.RequestError as e:
            log.error(f"Request Error: A request to Sharepoint failed. Error: {e}")
            raise e
        except httpx.HTTPStatusError as e:
            log.error(f"HTTP Status Error: Invalid HTTP status code received. Error: {e}")
            raise e
        except json.JSONDecodeError as e:
            log.error(f"Json Decode Error: The received JSON could not be decoded. Error: {e}")
            raise e

    return wrapper


@app.task(bind=True, autoretry_for=CONNECTION_ERRORS, default_retry_delay=60, max_retries=4)
@connection_error_handler
def write_ordermanagement(self, division):
    log.debug(f"Write Ordermanagement (start function). {division=}")
    try:
        rewrite_latest_orderbook_from_and_to_sharepoint(division=division)
        log.info(f"Orderbook for {division=} has been successfully written from and to Sharepoint.")
    except AssertionError as e:
        log.error(f"Assertion Error: A condition is not met. Error: {e}")
    except ValueError as e:
        if "drive with the name" in str(e):
            log.error(f"Value Error: Issue with drive name. Either multiple or no drive found. Error: {e}")
        else:
            log.error(f"Value Error: A parameter had an invalid value. Error: {e}")
    except AttributeError as e:
        log.error(f"Attribute Error: A nonexistent attribute was called. Error: {e}")


@app.task(bind=True, autoretry_for=CONNECTION_ERRORS, default_retry_delay=60, max_retries=4)
@connection_error_handler
def get_porz_plannings(self):
    import_porz_plans_from_sharepoint()
    log.info("PORZ plans have been successfully imported from Sharepoint.")
