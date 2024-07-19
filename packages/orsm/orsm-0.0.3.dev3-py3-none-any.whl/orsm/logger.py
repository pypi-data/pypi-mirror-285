#!/usr/bin/env python3
"""
Some wrapping around the default logging module.
"""

import logging
from orsm.variables import variable_names_and_objects
import sys
from haggis.logs import add_logging_level
from termcolor import colored
import os
from tqdm import tqdm
from functools import partial

add_logging_level('TRACE', logging.DEBUG - 5)
add_logging_level('PRINT', logging.WARNING - 5)


class MyFormatter(logging.Formatter):
    """A nice formatter for logging messages."""
    line_formatting = f" {colored('(%(pathname)s:%(lineno)d)', 'light_grey')}"
    timestamp_formatting = f"{colored('[%(asctime)s]: ', 'green')}"
    trace_format = f"{colored('TRACE', 'cyan')}: %(msg)s"
    debug_format = f"{colored('DEBUG', 'magenta')}: %(msg)s"
    info_format = f"{colored('INFO', 'blue')}: %(msg)s"
    print_format = f"%(msg)s"
    warning_format = f"{timestamp_formatting}{colored('WARNING', 'yellow')}:{line_formatting} %(msg)s"
    error_format = f"{timestamp_formatting}{colored('ERROR', 'red')}:{line_formatting} %(msg)s"
    critical_format = f"{timestamp_formatting}{colored('CRITICAL', 'red', attrs=['reverse', 'blink', 'bold'])}: {line_formatting} %(msg)s"

    def __init__(self):
        super().__init__(fmt=f"UNKNOWN: %(msg)s", datefmt=None, style='%')

    def format(self, record):

        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.TRACE:
            self._style._fmt = MyFormatter.trace_format
        elif record.levelno == logging.DEBUG:
            self._style._fmt = MyFormatter.debug_format
        elif record.levelno == logging.INFO:
            self._style._fmt = MyFormatter.info_format
        elif record.levelno == logging.PRINT:
            self._style._fmt = MyFormatter.print_format
        elif record.levelno == logging.WARNING:
            self._style._fmt = MyFormatter.warning_format
        elif record.levelno == logging.ERROR:
            self._style._fmt = MyFormatter.error_format
        elif record.levelno == logging.CRITICAL:
            self._style._fmt = MyFormatter.critical_format
        else:
            raise NotImplementedError(f"We don't know how to format logging levels: {record.levelno}")

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result


class StdOutFilter(logging.Filter):
    def filter(self, rec):
        return rec.levelno <= logging.PRINT


class StdErrFilter(logging.Filter):
    def filter(self, rec):
        stdout_filter = StdOutFilter()
        return not stdout_filter.filter(rec)


def set_logging_level(*, level):
    logging.root.setLevel(level)


log_file_extensions = {"stdout": ".stdout.log",
                       "stderr": ".stderr.log"}


def redirect_logging_to_file(*args, filename=None, **kwargs):
    if filename is None:
        filename = ""
    assert isinstance(filename, str) and " " not in filename, f"A nice filename is required, not: {filename = }"
    fmt = MyFormatter()
    stdout_handler = logging.FileHandler(f"{filename}{log_file_extensions['stdout']}", 'w+')
    stdout_handler.setFormatter(fmt)
    stdout_handler.addFilter(StdOutFilter())
    logging.root.addHandler(stdout_handler)
    stderr_handler = logging.FileHandler(f"{filename}{log_file_extensions['stderr']}", 'w+')
    stderr_handler.setFormatter(fmt)
    stderr_handler.addFilter(StdErrFilter())
    logging.root.addHandler(stderr_handler)


def setup_console_output():
    fmt = MyFormatter()
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(fmt)
    stdout_handler.addFilter(StdOutFilter())
    logging.root.addHandler(stdout_handler)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(fmt)
    stderr_handler.addFilter(StdErrFilter())
    logging.root.addHandler(stderr_handler)


def remove_console_output():
    if len(logging.root.handlers) >= 2:
        # We assume the console handlers are the first two.
        del logging.root.handlers[:2]


def suppress_console_output():
    fmt = MyFormatter()
    null = open(os.devnull, 'w')
    stdout_handler = logging.StreamHandler(null)
    stdout_handler.setFormatter(fmt)
    stdout_handler.addFilter(StdOutFilter())
    logging.root.addHandler(stdout_handler)
    stderr_handler = logging.StreamHandler(null)
    stderr_handler.setFormatter(fmt)
    stderr_handler.addFilter(StdErrFilter())
    logging.root.addHandler(stderr_handler)


set_logging_level(level=logging.PRINT)
setup_console_output()  # A nice default setup.
# NB: I don't think this needs the python equivalent of a header guard: https://stackoverflow.com/a/2950584/5134817
logging.DEFAULT_LEVEL = logging.PRINT

log = logging

progressbar = partial(tqdm, leave=False)
# We put this here as we may also want to log some of these results...

if __name__ == "__main__":
    # A very small demo.
    from time import sleep

    set_logging_level(level=logging.TRACE)
    for name, logger in variable_names_and_objects(log.trace, log.debug, log.info, log.print, log.warning, log.error, log.critical):
        sleep(0.01)  # So we can see the timestamp increments more clearly.
        logger(f"A message from {name}")
