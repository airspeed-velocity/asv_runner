# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
Various low-level utilities.
"""

import math
import shutil

terminal_width = shutil.get_terminal_size().columns


def ceildiv(numerator, denominator):
    """Ceiling division"""
    return -((-numerator) // denominator)


def human_float(value, significant=3, truncate_small=None, significant_zeros=False):
    """
    Return a string representing a float with human friendly significant digits.
    Switches to scientific notation for too large/small numbers.
    If `truncate_small`, then leading zeros of numbers < 1 are counted as
    significant. If not `significant_zeros`, trailing unnecessary zeros are
    stripped.
    """
    if value == 0:
        return "0"
    elif math.isinf(value) or math.isnan(value):
        return f"{value}"
    elif value < 0:
        sign = "-"
        value = -value
    else:
        sign = ""

    logv = math.log10(value)
    magnitude = int(math.floor(logv)) + 1

    if truncate_small is not None:
        magnitude = max(magnitude, -truncate_small + 1)

    num_digits = significant - magnitude

    if magnitude <= -5 or magnitude >= 9:
        # Too many digits, use scientific notation
        fmt = f"{{0:.{significant}e}}"
    elif value == int(value):
        value = int(round(value, num_digits))
        fmt = "{0:d}"
    elif num_digits <= 0:
        value = int(round(value, num_digits))
        fmt = "{0:d}"
    else:
        fmt = f"{{0:.{num_digits}f}}"

    formatted = sign + fmt.format(value)

    if not significant_zeros and "." in formatted and "e" not in fmt:
        formatted = formatted.rstrip("0")
        if formatted[-1] == ".":
            formatted = formatted[:-1]

    if significant_zeros and "." not in formatted:
        if len(formatted) < significant:
            formatted += "." + "0" * (significant - len(formatted))

    return formatted


_human_time_units = (
    ("ns", 0.000000001),
    ("μs", 0.000001),
    ("ms", 0.001),
    ("s", 1),
    ("m", 60),
    ("h", 60 * 60),
    ("d", 60 * 60 * 24),
    ("w", 60 * 60 * 24 * 7),
    ("y", 60 * 60 * 24 * 7 * 52),
    ("C", 60 * 60 * 24 * 7 * 52 * 100),
)


def human_time(seconds, err=None):
    """
    Returns a human-friendly time string that is always exactly 6
    characters long.

    Depending on the number of seconds given, can be one of::

        1w 3d
        2d 4h
        1h 5m
        1m 4s
          15s

    Will be in color if console coloring is turned on.

    Parameters
    ----------
    seconds : int
        The number of seconds to represent

    Returns
    -------
    time : str
        A human-friendly representation of the given number of seconds
        that is always exactly 6 characters.
    """
    units = _human_time_units
    seconds = float(seconds)

    scale = seconds

    if scale == 0 and err is not None:
        scale = float(err)

    if scale == 0:
        # Represent zero in reasonable units
        units = [("s", 1), ("m", 60)]

    if scale != scale:
        # nan
        return "n/a"

    for i in range(len(units) - 1):
        if scale < units[i + 1][1]:
            str_time = human_float(seconds / units[i][1], 3, significant_zeros=True)
            if err is None:
                return f"{str_time:s}{units[i][0]}"
            else:
                str_err = human_float(err / units[i][1], 1, truncate_small=2)
                return f"{str_time:s}±{str_err:s}{units[i][0]}"
    return "~0"
