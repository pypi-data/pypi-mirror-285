import logging
import functools
import inspect
import pandas as pd
import json
import sys
import time
import urllib

from collections import Counter
from pathlib import Path
from logging import Logger
from typing import Dict, Optional
from sempy._version import get_versions
from sempy.fabric._token_provider import _get_token_seconds_remaining, _get_token_expiry_utc

SEMPY_LOGGER_NAME = "SemPy"
MDS_LOG_TABLE = "SynapseMLLogs"

mds_fields: dict = {}


def _get_type_name(obj):
    t = type(obj)
    return t.__module__ + "." + t.__name__


def _scrub(msg, opening, closing):
    result = ""
    msg_current = 0
    msg_end = len(msg)
    hit_start = msg.find(opening)
    while hit_start >= 0:
        hit_end = msg.find(closing, hit_start + len(opening))
        if hit_end >= 0:
            result += msg[msg_current: hit_start + len(opening)]
            result += "REDACTED"
            result += closing
            msg_current = hit_end + len(closing)
            hit_start = msg.find(opening, msg_current)
        else:
            # If we don't find the closing marker, then append the rest. We've seen accidentally
            # shortened messages that did not have a lot of detail.
            hit_start = -1
    result += msg[msg_current: msg_end]
    return result


def _initialize_log(
        on_fabric: bool,
        env: str,
        notebook_workspace_id: str,
        artifact_id: str,
        artifact_type: str
):
    global mds_fields

    mds_fields = {
        "mds_ComponentName": "SemPy",
        "mds_TelemetryApplicationInfo": {
            "ApplicationName": "SemPy",
            "ApplicationType": "python",
            "ApplicationVersion": get_versions()['version'],
            "ArtifactId": artifact_id,
            "ArtifactType": artifact_type
        },
        "mds_Workspace": notebook_workspace_id
    }

    if on_fabric:
        from synapse.ml.pymds.handler import SynapseHandler

        # Use the pymds decorator after it's aligned with the one we have here
        # from synapse.ml.pymds.synapse_logger import DecoratorJSONFormatter

        logger = logging.getLogger(SEMPY_LOGGER_NAME)
        logger.setLevel(logging.DEBUG)
        handler = SynapseHandler(MDS_LOG_TABLE, scrubbers=[])
        handler.setFormatter(ScrubbingFormatter() if env == "prod" else DecoratorJSONFormatter())
        logger.addHandler(handler)
        logger.propagate = False


# ---------------- Begin code originating from Synapse-Utils (synapse_logger.py) ----------------------
# This version of the decorator avoids duplication of file_name, lineno, levelname, Throwable that is the
# feature of the current pymds version. As a result Message column is more compact and readable.


class DecoratorJSONFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord):
        if isinstance(record.args, dict):
            if 'func_name_override' in record.args:
                record.funcName = record.args['func_name_override']
            if 'file_name_override' in record.args:
                record.filename = record.args['file_name_override']
            if 'path_name_override' in record.args:
                record.pathname = record.args['path_name_override']
            if 'lineno_override' in record.args:
                record.lineno = record.args['lineno_override']
            if 'module_override' in record.args:
                record.module = record.args['module_override']

        return json.dumps(record.msg)

    def formatException(self, exc_info):
        """
        Override the default formatException to place exception type and error first.

        Also, inverts the stack sequence to go from top to bottom while skipping
        irrelelevant information.
        """
        import linecache

        error_message = str(exc_info[1])
        formatted_traceback = f"{exc_info[0].__name__}: {error_message}\n\nTraceback:"

        tb = exc_info[2]
        while tb is not None:
            function_name = tb.tb_frame.f_code.co_name
            line_number = tb.tb_lineno
            filename = tb.tb_frame.f_code.co_filename
            marker = 'site-packages/'
            idx = filename.find(marker)
            if idx > 0:
                filename = filename[idx + len(marker):]

            context_line = linecache.getline(filename, line_number).strip()

            if function_name != "log_decorator_wrapper":
                formatted_traceback += f'\nFile "{filename}", line {line_number}, in {function_name}'
                formatted_traceback += f'\n    {context_line}'

            tb = tb.tb_next

        return formatted_traceback


# ---------------- End code originating from Synapse-Utils (synapse_logger.py) ----------------------

class ScrubbingFormatter(DecoratorJSONFormatter):
    """
    We need to differentiate scrubbing depending on where the exception was raised from,
    so we place scrubbing in the decorator, where we have access to the exception details.
    The IScrub implementation of pymds, applies simple string replacement based solely on
    the message text.
    """
    def format(self, record: logging.LogRecord):
        msg = super().format(record)
        return _scrub(msg, "'", "'")

    def formatException(self, exc_info):
        formatted_traceback = super().formatException(exc_info)
        if _get_type_name(exc_info[1]) == "System.AggregateException":
            # Exception originating from .NET (e.g. XMLA clients, Parquet) are usually AggregateExceptions.
            # They place single quotes around valuable information such as class names, so we cannot use the single
            # quote scrubbing that we use for our internal exceptions. Meanwhile, DAX displays the the query
            # between XML tags "<ccon>".
            return _scrub(formatted_traceback, "<ccon>", "</ccon>")
        else:
            return _scrub(formatted_traceback, "'", "'")


# ---------------- Begin code originating from Synapse-Utils (decorator.py) ----------------------

class MdsExtractor:
    """
    Base extraction class used for standard logging.

    Parameters
    ----------
    logger : Logger
        Logger object used for telemetry.
    """
    def __init__(self, logger: Optional[Logger] = None):
        if logger is None:
            self.logger = logging.getLogger("decorator")
        else:
            self.logger = logger

        self.start_time = time.perf_counter()

    def get_initialization_mds_fields(self) -> Dict:
        """
        Returns the columns used for telemetry (prefixed with "mds").
        Executes BEFORE function execution.

        Returns
        -------
        Dict
            Mds column identifiers and their values.
        """
        return {}

    def get_completion_message_dict(self, result, arg_dict) -> Dict:
        """
        Returns dictionary of key/value pairs that will be present in the log message.
        Executes AFTER function execution.

        Parameters
        ----------
        result : Any
            Object returned from function execution.
        arg_dict : Dict
            Arguments passed to function.

        Returns
        -------
        Dict[str, str]
            Additional message key/value pairs.
        """
        return {}

    def get_execution_time(self, digits: int = 3) -> float:
        """
        Returns how long the function took to execute, based on provided start time.

        Parameters
        ----------
        digits : int, default=3
            How many significant digits to round result to.

        Returns
        -------
        float
            Execution time in seconds, rounded to provided significant digits.
        """
        from math import log10, floor
        exec_time = time.perf_counter() - self.start_time
        # round to significant digits
        return round(exec_time, digits-int(floor(log10(abs(exec_time))))-1)


def mds_log(extractor: MdsExtractor = MdsExtractor(), log_level: int = logging.INFO):

    # logger = get_mds_json_logger("decorator") if logger is None else logger

    def get_wrapper(func):

        path_name_override = sys._getframe().f_back.f_code.co_filename
        file_name_override = Path(path_name_override).name
        lineno_override = sys._getframe().f_back.f_lineno

        @functools.wraps(func)
        def log_decorator_wrapper(*args, **kwargs):

            saved_log_level = extractor.logger.level
            extractor.logger.setLevel(log_level)

            extra = {
                "log_kusto": True,
                "func_name_override": func.__name__,
                "module_override": func.__module__,
                "file_name_override": file_name_override,
                "path_name_override": path_name_override,
                "lineno_override": lineno_override
            }

            message = {"func": f"{func.__module__}.{func.__name__}"}

            try:
                extra.update(extractor.get_initialization_mds_fields())

                s = inspect.signature(func)
                arg_dict = s.bind(*args, **kwargs).arguments

            except Exception:
                extractor.logger.error(message, extra, exc_info=True)
                extractor.logger.setLevel(saved_log_level)
                raise

            try:
                result = func(*args, **kwargs)

                # The invocation for get_message_dict moves after the function
                # so it can access the state after the method call
                message.update(extractor.get_completion_message_dict(result, arg_dict))

                message["total_seconds"] = extractor.get_execution_time()

                # We are passing a dict in "message", even though the python logger docstrings state
                # that it will interpret it as a % format string, e.g. "Log 'msg % args' with severity 'INFO'".
                # The current design is thus a hack that flies only due to the lack of strong typing and
                # could cause more problems. If so, we could redesign to have Extractors output a string,
                # reducing future options for handlers/formatters.
                extractor.logger.info(message, extra)
            except Exception:
                # get_message_dict itself could be the cause of the exception, which we have to catch
                # if we want to get a chance to log the original exception details
                try:
                    message.update(extractor.get_completion_message_dict(None, arg_dict))
                except Exception as e:
                    message["extract_message_error_type"] = type(e).__name__
                    message["extract_message_error_text"] = str(e)
                message["total_seconds"] = extractor.get_execution_time()
                extractor.logger.error(message, extra, exc_info=True)
                raise
            finally:
                extractor.logger.setLevel(saved_log_level)
            return result

        return log_decorator_wrapper

    return get_wrapper


# ----------- End code originating from Synapse-Utils  ----------------------

class SemPyExtractor(MdsExtractor):
    """
    Base extraction class used for standard SemPy logging. Has logic for redacting and formatting values.
    """

    def __init__(self):
        self.logger = logging.getLogger(SEMPY_LOGGER_NAME)
        super().__init__(self.logger)

    def get_initialization_mds_fields(self) -> Dict:
        global mds_fields
        return mds_fields

    def get_completion_message_dict(self, result, arg_dict) -> Dict:
        d: dict = {}

        for arg, value in arg_dict.items():
            if isinstance(value, str):
                # Long strings and string that contain quotes should not be logged.
                # Quotes can interfere with redaction and JSON formatting.
                if len(value) > 40 or "'" in value or '"' in value:
                    d[arg] = 'REDACTED'
                else:
                    # Percentage sign is used by python logging as a formatting directive 'msg % args'
                    # and needs to be escaped before sending it to logger's info/error:
                    d[arg] = f"'{value}'".replace('%', '%%')
            elif isinstance(value, (int, float)):  # includes bool, which is an int
                d[arg] = value
            elif isinstance(value, pd.DataFrame):
                d[f"{arg}.type"] = _get_type_name(value)
                d[f"{arg}.shape"] = value.shape

        # Functions that do not return anything have the result of "None",
        # which will fail the tests on hasattr(). The result will thus
        # not appear in the dictionary and the message:
        if hasattr(result, 'shape'):
            d['result.shape'] = result.shape
        elif hasattr(result, '__len__'):
            d['result.len'] = len(result)

        return d


class TablesExtractor(SemPyExtractor):
    """
    Extraction class used for logging functions which have tables in the result.
    """

    def get_completion_message_dict(self, result, arg_dict) -> Dict:
        d = super().get_completion_message_dict(result, arg_dict)
        tables = arg_dict.get('tables')
        if isinstance(tables, dict):
            element_types = [_get_type_name(o) for o in tables.values()]
        elif isinstance(tables, list):
            element_types = [_get_type_name(o) for o in tables]
        else:
            element_types = _get_type_name(tables)
        d['tables'] = Counter(element_types)
        return d


class RetryExtractor(SemPyExtractor):
    """
    Extraction class used for logging REST retries.
    """

    def get_completion_message_dict(self, result, arg_dict) -> Dict:
        d = super().get_completion_message_dict(result, arg_dict)
        response = arg_dict['kwargs'].get('response')
        retry_obj = arg_dict['self']
        d['total'] = retry_obj.total
        d['backoff_time'] = retry_obj.get_backoff_time()
        d['retry_after'] = retry_obj.get_retry_after(response)
        d['is_exhausted'] = retry_obj.is_exhausted()
        if response is not None:
            if getattr(response, 'status', None) is not None:
                d['status_code'] = response.status
            if getattr(response, 'url', None) is not None:
                d['url'] = urllib.parse.unquote(response.url)
            if getattr(response, 'headers', None) is not None:
                d['request_id'] = response.headers.get('RequestId', None)
            if getattr(response, 'data', None) is not None:
                d['response_text'] = urllib.parse.unquote(response.data.decode('utf-8', errors='backslashreplace'))
        return d


class RestRequestExtractor(SemPyExtractor):
    """
    Extraction class used for logging REST requests.
    """

    def get_completion_message_dict(self, result, arg_dict) -> Dict:
        d = super().get_completion_message_dict(result, arg_dict)
        headers = result.headers
        d['method'] = result.method
        token = headers['authorization'].split("Bearer ")[1]
        d['token_seconds_remaining'] = _get_token_seconds_remaining(token)
        d['token_expiry_time'] = _get_token_expiry_utc(token)
        # useful for local token debugging
        # import hashlib
        # d['encrypted_token'] = hashlib.sha256(token.encode("utf-8")).hexdigest()
        if result.url:
            d['url'] = urllib.parse.unquote(result.url)
        # Generated by SemPy, correlates to ClientActivityId in Kusto
        d['activity_id'] = headers.get('ActivityId', None)
        return d


class RestResponseExtractor(SemPyExtractor):
    """
    Extraction class used for logging REST responses.
    """

    def get_completion_message_dict(self, result, arg_dict) -> Dict:
        d = super().get_completion_message_dict(result, arg_dict)
        response = arg_dict['response']
        d['status_code'] = response.status_code
        # Generated by PBI service, correlates to RootActivityId in Kusto
        d['request_id'] = response.headers.get("RequestId", None)
        return d


class XmlaExtractor(SemPyExtractor):
    """
    Extraction class used for logging XMLA operations.
    This sets up the relevant correlation ID using Trace.CorrelationManager.
    """

    def get_initialization_mds_fields(self) -> Dict:
        from System.Diagnostics import Trace
        from System import Guid

        # set xmla correlation id before function execution
        Trace.CorrelationManager.ActivityId = Guid.NewGuid()
        return super().get_initialization_mds_fields()

    def get_completion_message_dict(self, result, arg_dict) -> Dict:
        d = super().get_completion_message_dict(result, arg_dict)

        from System.Diagnostics import Trace
        from System import Guid

        # get the guid we set during initialization
        d["activity_id"] = Trace.CorrelationManager.ActivityId.ToString()

        # reset activity id after function execution
        Trace.CorrelationManager.ActivityId = Guid.NewGuid()

        return d


log = mds_log(SemPyExtractor())
log_error = mds_log(SemPyExtractor(), logging.ERROR)
log_retry = mds_log(RetryExtractor())
log_tables = mds_log(TablesExtractor())
log_rest_request = mds_log(RestRequestExtractor(), logging.ERROR)
log_rest_response = mds_log(RestResponseExtractor(), logging.ERROR)
log_xmla = mds_log(XmlaExtractor())
