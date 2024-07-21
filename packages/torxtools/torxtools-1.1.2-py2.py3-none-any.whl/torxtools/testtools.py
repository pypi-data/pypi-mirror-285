"""
Functions for working with unit tests.

"""

import contextlib
import sys
import typing as t

__all__: t.List[str] = [
    "disable_outputs",
]


@contextlib.contextmanager
def disable_outputs():
    """
    stack overflow programming
    https://stackoverflow.com/questions/1809958/hide-stderr-output-in-unit-tests
    """
    prev_stdout = sys.stdout
    prev_stderr = sys.stderr

    class DevNull:
        def write(self, _):
            pass

        def flush(self):
            pass

    sys.stdout = DevNull()
    sys.stderr = DevNull()
    try:
        yield
    finally:
        sys.stdout = prev_stdout
        sys.stderr = prev_stderr
