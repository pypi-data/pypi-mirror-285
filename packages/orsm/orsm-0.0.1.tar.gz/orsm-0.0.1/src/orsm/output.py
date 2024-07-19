"""
Handling output.
"""

import py


class Suppressor(object):
    """A class to suppress printing output."""

    def __init__(self, *, suppress_output=True):
        self.suppress_output = suppress_output

    def __enter__(self):
        if self.suppress_output:
            """
            The only method I have found which can 
            suppress all output from Python and C
            extensions is to have the a C extension
            do all the redirection of stdout/stderr.
            
            It is the C extensions which case all the problems!
            """
            self.capture = py.io.StdCaptureFD()  # Captures everything from Python

    def __exit__(self, *args):
        if self.suppress_output:
            self.capture.reset()
