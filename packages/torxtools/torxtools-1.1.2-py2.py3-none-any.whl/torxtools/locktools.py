import base64
import functools
import tempfile

from filelock import FileLock, Timeout

__all__ = []


def critical_section(fn=None, *, name=None, timeout=0, callback=None):
    def _critical_section(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # Generate a name and use it as a filename
            if name:
                qualname = name
            else:
                qualname = f"{fn.__module__}.{fn.__qualname__}"
            qualname = base64.b64encode(qualname.encode("UTF-8")).decode("UTF-8")

            filename = tempfile.gettempdir() + "/filelock-" + qualname + ".lock"

            lock = FileLock(filename)
            try:
                with lock.acquire(timeout=timeout):
                    return fn(*args, **kwargs)
            except Timeout:
                if callback:
                    return callback()

                raise PermissionError("Function is already in use and is locked") from None

        return wrapper

    if fn:
        return _critical_section(fn)

    return _critical_section
