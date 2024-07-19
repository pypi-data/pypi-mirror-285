#!/usr/bin/env python3

import unittest
from orsm.logger import log, set_logging_level, log_file_extensions
from orsm.variables import variable_names_and_objects
import sys
from subprocess import Popen, PIPE
import cli_print_logs
from testfixtures import LogCapture
import shlex
from tempfile import TemporaryDirectory
import os
import pathlib


class Logger(unittest.TestCase):
    def test_regular_output(self):
        names_and_messages = {}
        with LogCapture(level=log.PRINT) as l:
            for name, logger in variable_names_and_objects(log.trace, log.debug, log.info, log.print, log.warning, log.error, log.critical, vars_only=True):
                message = f"A message from {name}"
                logger(message)
                if log.getLevelNamesMapping()[name.upper()] >= log.PRINT:
                    names_and_messages[name] = message
        l.check(*[('root', name.upper(), message) for name, message in names_and_messages.items()])

    def test_all_output(self):
        names_and_messages = {}
        with LogCapture() as l:
            set_logging_level(level=log.TRACE)
            for name, logger in variable_names_and_objects(log.trace, log.debug, log.info, log.print, log.warning, log.error, log.critical, vars_only=True):
                message = f"A message from {name}"
                logger(message)
                names_and_messages[name] = message
        l.check(*[('root', name.upper(), message) for name, message in names_and_messages.items()])


class LoggerVerbosity(unittest.TestCase):

    def test_output_from_cli_regular(self):
        command = shlex.split(f"{sys.executable} {cli_print_logs.__file__}")
        p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate(b"")
        rc = p.returncode
        self.assertEqual(rc, 0, f"We were unable to run the subprocess {command = }, encountering\noutput:\n{output=}\nerror:\n{err}")
        for name, logger in variable_names_and_objects(log.trace, log.debug, log.info, log.print, log.warning, log.error, log.critical, vars_only=True):
            message = f"A message from {name}"
            if log.getLevelNamesMapping()[name.upper()] > log.DEFAULT_LEVEL:
                self.assertIn(message, err.decode())
            elif log.getLevelNamesMapping()[name.upper()] == log.DEFAULT_LEVEL:
                self.assertIn(message, output.decode())
            else:
                self.assertNotIn(message, output.decode())
                self.assertNotIn(message, err.decode())

    def test_output_from_cli_level(self):
        flags_and_levels = {"--trace": log.TRACE,
                            "--verbose": log.INFO,
                            "--debug": log.DEBUG,
                            "--quiet": log.WARNING,
                            "--silent": log.ERROR}
        for flag, level in flags_and_levels.items():
            command = shlex.split(f"{sys.executable} {cli_print_logs.__file__} {flag}")
            p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate(b"")
            rc = p.returncode
            self.assertEqual(rc, 0, f"We were unable to run the subprocess {command = } with {flag = }, encountering\noutput:\n{output=}\nerror:\n{err}")
            all_output = "".join([i.decode() for i in [output, err]])
            for name, logger in variable_names_and_objects(log.trace, log.debug, log.info, log.print, log.warning, log.error, log.critical, vars_only=True):
                message = f"A message from {name}"
                if log.getLevelNamesMapping()[name.upper()] >= level:
                    self.assertIn(message, all_output)
                else:
                    self.assertNotIn(message, all_output)

    def test_no_output_when_suppressed(self):
        command = shlex.split(f"{sys.executable} {cli_print_logs.__file__} --suppress_console_output")
        p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate(b"")
        rc = p.returncode
        self.assertEqual(rc, 0, f"We were unable to run the subprocess {command = }, encountering\noutput:\n{output=}\nerror:\n{err}")
        self.assertFalse(output)
        self.assertFalse(err)

    def test_output_files_produced(self):
        file_names = ["", "foo"]
        for file_name in file_names:
            with TemporaryDirectory() as temp_directory:
                expected_files = [pathlib.Path(f"{os.path.join(temp_directory, file_name)}{extension}") for extension in log_file_extensions.values()]
                command = shlex.split(f"{sys.executable} {cli_print_logs.__file__} --trace --log_files {file_name}")
                p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=temp_directory)
                output, err = p.communicate(b"")
                rc = p.returncode
                self.assertEqual(rc, 0, f"We were unable to run the subprocess {command = }, encountering\noutput:\n{output=}\nerror:\n{err}")
                for file in expected_files:
                    self.assertTrue(file.is_file(), f"We cant find the file: {file}")
                    self.assertGreater(os.path.getsize(file), 0, f"The {file = } is expected to be non-empty.")


if __name__ == '__main__':
    unittest.main()
