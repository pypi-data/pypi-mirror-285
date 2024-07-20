# encoding: utf-8
import time
import warnings
from typing import *
import numpy as np

num_type = int | float

decimal_dtype = ['int32', 'int64', 'float32', 'float64']


def multi_split(string: str, seps: list[str] | tuple[str] | None = None) -> list:
    """
    Splits a string using given separators, but supports multiple separators in comparison with
    the built_in method str.split, as it only supports a single separator.

    Notes:
        Would raise warning if one sep is part of another sep, as the results are unpredictable.

    Args:
        string (str): the string being splitted
        seps (list[str] | tuple[str] | None): the separators used for splitting

    Returns:
        list: string after splitting
    """

    # raise warning if one sep is part of another sep
    for i in range(len(seps)):
        for j in range(len(seps)):
            if seps[i] in seps[j] and i != j:
                warnings.warn('sep {0} is part of sep {1}, this might cause unexpected results'.
                              format(repr(seps[i]), repr(seps[j])))

    last = -1
    lst = []
    seps.sort()  # sort to put longer seps first for testing

    for i in range(len(string)):
        for j in range(len(seps)):
            # skip if sep is longer than remaining characters
            if i + len(seps[j]) > len(string) or last >= i:
                continue

            if string[i:i + len(seps[j])] == seps[j]:
                lst.append(string[last + 1:i])
                last = i + len(seps[j]) - 1

            # test again at the end of the string
            elif i == len(string) - 1:
                lst.append(string[last + 1:])

    return lst


def cnt_add(cnt: dict[Any, int], value: Hashable) -> dict[any, int]:
    """
    Return counting dictionary with value added 1, can be replaced using collections.Counter.
    """
    if value in cnt.keys():
        cnt[value] += 1
    else:
        cnt[value] = 1
    return cnt


def isempty(obj: Any) -> bool:
    empty_values = [[], '', {}, (), None]  # known empty values

    if obj in empty_values:
        return True
    return False


def isdecimal(string: str) -> bool:
    """
    Test whether the string is a decimal, as str.isdigit and others don't test decimals,
    only integers.

    Args:
        string (str): the string to test

    Returns:
        bool: the test results
    """
    # only numbers can be converted to float
    try:
        float(string)
    except ValueError as _:
        return False

    return True


# noinspection PyStatementEffect
def program_counter(funcs: list | tuple, repeat: int = 1000) -> tuple[list[float], int]:
    """
    Counts the runtime for each function given, recommend using lambda if function needs parameters.

    Args:
        funcs (list | tuple): contains the functions to use
        repeat (int): times to repeat each function

    Returns:
        list[float]: the runtimes of the functions
    """

    times = []
    for i in funcs:
        t1 = time.perf_counter()  # more precise than others like time.time
        for _ in range(repeat):
            i()
        t2 = time.perf_counter()
        # minus runtime of time.perf_counter for accuracy
        times.append((t2 - t1 + time.perf_counter()-time.perf_counter())/repeat)
    return times, np.argmin(times)[0]
