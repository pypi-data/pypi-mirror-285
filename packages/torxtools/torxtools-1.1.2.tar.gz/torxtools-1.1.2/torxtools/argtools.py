"""
Parser types for command-line options, arguments and sub-commands

"""

import os
import typing as t
from argparse import ArgumentTypeError

__all__ = [
    "is_int_positive",
    "is_int_positive_or_zero",
    "is_int_negative",
    "is_int_negative_or_zero",
    "is_file",
    "is_dir",
]


def _get_int_number(value: int, message: str) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ArgumentTypeError(message) from None


def is_int_positive(value: int) -> int:
    """
    Verify that argument passed is a positive integer.

    Parameters
    ----------
    value: int
        value passed from argparser

    Returns
    -------
    int
        value passed from argparser

    Example
    -------

    .. code-block::

        parser.add_argument(
            "--size", "-s",
            dest="size",
            help="[MB] Minimal size of attachment",
            type=torxtools.argtools.is_int_positive,
            default=100,
        )
    """
    message = f"value '{value}' must be positive"
    number = _get_int_number(value, message)
    if number <= 0:
        raise ArgumentTypeError(message) from None
    return number


def is_int_positive_or_zero(value: int) -> int:
    """
    Verify that argument passed is a positive integer or zero.

    Parameters
    ----------
    value: int
        value passed from argparser

    Returns
    -------
    int
        value passed from argparser

    Example
    -------

    .. code-block::

        parser.add_argument(
            "--size", "-s",
            dest="size",
            help="[MB] Minimal size of attachment",
            type=torxtools.argtools.is_int_positive_or_zero,
            default=100,
        )
    """
    message = f"value '{value}' must be positive or zero"
    number = _get_int_number(value, message)
    if number < 0:
        raise ArgumentTypeError(message) from None
    return number


def is_int_negative(value: int) -> int:
    """
    Verify that argument passed is a negative integer.

    Parameters
    ----------
    value: int
        value passed from argparser

    Returns
    -------
    int
        value passed from argparser

    Example
    -------

    .. code-block::

        parser.add_argument(
            "--temperature", "-t",
            dest="temperature",
            help="[C] Temperature colder than freezing point",
            type=torxtools.argtools.is_int_negative,
            default=-50,
        )
    """
    message = f"value '{value}' must be negative"
    number = _get_int_number(value, message)
    if number >= 0:
        raise ArgumentTypeError(message) from None
    return number


def is_int_negative_or_zero(value: int) -> int:
    """
    Verify that argument passed is a negative integer or zero.

    Parameters
    ----------
    value: int
        value passed from argparser

    Returns
    -------
    int
        value passed from argparser

    Example
    -------

    .. code-block::

        parser.add_argument(
            "--temperature", "-t",
            dest="temperature",
            help="[C] Temperature colder than freezing point",
            type=torxtools.argtools.is_int_negative_or_zero,
            default=-50,
        )
    """
    message = f"value '{value}' must be negative or zero"
    number = _get_int_number(value, message)
    if number > 0:
        raise ArgumentTypeError(message) from None
    return number


def is_file(value: str) -> t.Callable:
    """
    Returns path if path is an existing regular file.
    This follows symbolic links

    Parameters
    ----------
    value: str
        value passed from argparser

    Returns
    -------
    str
        value passed from argparser

    Example
    -------

    .. code-block::

        parser.add_argument(
            "-f", "--file"
            type=torxtools.argtools.is_file
        )
    """
    message = f"value '{value}' must be an existing file"
    if not os.path.isfile(str(value)):
        raise ArgumentTypeError(message) from None
    return value


def is_not_dir(value: str) -> t.Callable:
    """
    Returns path if path is an existing file, including devices and not a directory.

    Parameters
    ----------
    value: str
        value passed from argparser

    Returns
    -------
    str
        value passed from argparser

    Example
    -------

    .. code-block::

        parser.add_argument(
            "-f", "--file"
            type=torxtools.argtools.is_file
        )
    """
    message = f"value '{value}' must be an existing file"
    value = str(value)
    if not os.path.exists(str(value)):
        raise ArgumentTypeError(message) from None
    if os.path.isdir(str(value)):
        raise ArgumentTypeError(message) from None
    return value


def is_dir(value: str) -> t.Callable:
    """
    Returns path if path is an existing regular directory.
    This follows symbolic links

    Parameters
    ----------
    value: str
        value passed from argparser

    Returns
    -------
    str
        value passed from argparser

    Example
    -------

    .. code-block::

        parser.add_argument(
            "-f", "--dir"
            type=torxtools.argtools.is_dir
        )
    """
    message = f"value '{value}' must be an existing directory"
    if not os.path.isdir(str(value)):
        raise ArgumentTypeError(message) from None
    return value
