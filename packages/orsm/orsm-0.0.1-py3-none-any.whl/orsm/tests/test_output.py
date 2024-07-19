#!/usr/bin/env python3
"""
Trying to test that we capture standard output.

NB - I am not so sure these tests are very well formed, as
we are trying to nest standard captures and I don't
think I have perfectly understood how to do this. One of the
difficulties is also with C extensions.
"""

import unittest

from orsm.output import Suppressor
import io
import sys
import contextlib


class SuppressorTest(unittest.TestCase):
    def test_no_suppressor_stdout(self):
        expect_output = "Something"
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            print(expect_output)
        self.assertTrue(expect_output in f.getvalue())

    def test_no_suppressor_stderr(self):
        expect_output = "Something"
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            print(expect_output, file=sys.stderr)
        self.assertTrue(expect_output in f.getvalue())

    def test_suppressor_stdout(self):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            with Suppressor(suppress_output=True):
                print("Something to stdout", )
                print("Something to stderr", file=sys.stderr)
        self.assertFalse(f.getvalue())

    def test_suppressor_stderr(self):
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            with Suppressor(suppress_output=True):
                print("Something to stdout", )
                print("Something to stderr", file=sys.stderr)
        self.assertFalse(f.getvalue())


if __name__ == '__main__':
    unittest.main()
