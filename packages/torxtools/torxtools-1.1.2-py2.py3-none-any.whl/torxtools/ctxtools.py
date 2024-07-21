"""
Utilities for with-statement contexts
"""

# pylint: disable=invalid-name
import contextlib
import sys


class suppress_traceback(contextlib.AbstractContextManager):
    """
    Context handler to suppress tracebacks and pretty print an error.

    In case exception is KeyboardInterrupt, then the error is suppressed.
    No assumption, error or normal exit, is made for why Ctrl-C was used.

    Example
    -------

    .. code-block::

        if __name__ == "__main__":
            with suppress_traceback():
                main()
    """

    def __init__(self, keyboard_exitcode=1, system_exitcode=1, error_exitcode=1):
        self.keyboard_exitcode = keyboard_exitcode
        self.system_exitcode = system_exitcode
        self.error_exitcode = error_exitcode

    def __exit__(self, exctype, excinst, _exctb):
        if exctype is None:
            return True

        if issubclass(exctype, KeyboardInterrupt):
            # exit code could be success or error, it all depends on if it's the
            # normal way of quitting the app, so eat the exception by default.
            sys.exit(self.keyboard_exitcode)

        if issubclass(exctype, SystemExit):
            # sys.exit was called with an exit-code, then re-raise with value
            with contextlib.suppress(ValueError, TypeError):
                code = int(excinst.code)
                sys.exit(code)

            # sys.exit was called with an message, print and re-reaise with error
            print(excinst, file=sys.stderr)
            sys.exit(self.system_exitcode)

        print(f"error: {excinst}", file=sys.stderr)
        sys.exit(self.error_exitcode)


class suppress(contextlib.suppress, contextlib.ContextDecorator):
    """
    A version of contextlib.suppress with decorator support.

    Example
    -------

    .. code-block::

        @contextlib.suppress(ValueError)
        def foobar():
            ...
    """


class reraise_from_none(contextlib.suppress, contextlib.ContextDecorator):
    """
    Similar to contextlib.suppress, but with decorator support, and that
    re-raises exception from None instead of hiding it.

    Example
    -------

    .. code-block::

        @contextlib.reraise_from_none(ValueError)
        def foobar():
            ...
    """

    def __exit__(self, exctype, excinst, _exctb):
        if exctype is None:
            return
        if issubclass(exctype, self._exceptions):
            raise excinst from None
