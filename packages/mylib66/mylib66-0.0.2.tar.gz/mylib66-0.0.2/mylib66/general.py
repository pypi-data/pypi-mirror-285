# encoding: utf-8
import copy
import itertools
import time
import warnings
from typing import *

import matplotlib.pyplot as plt
import numpy as np

num_type = int | float

decimal_dtype = ['int32', 'int64', 'float32', 'float64']


def removed(lst: list, values: Any, multiple: bool = False) -> list:
    """
    Return the list with given values removed.

    Args:
        lst (list): the list to be modified
        values (Any): the values to be removed
        multiple (bool): whether to read values as a sequence

    Returns:
        list: lst after given values removed
    """

    if not multiple:
        values = [values]

    result_lst = []
    for item in lst:
        if item not in values:
            result_lst.append(item)

    return result_lst


def drop(lst: list, index: list[int] | tuple[int] | int) -> list:
    """
    Return the list with given indexes removed.

    Args:
        lst (list): the list to be modified
        index (list[int] | tuple[int] | int): the indexes to be removed

    Returns:
        list: lst after given values removed
    """

    new_lst = []

    if type(index) is int:
        index = [index]

    for i in range(len(lst)):
        if i not in index:
            new_lst.append(lst[i])

    return new_lst


def type_same(lst: list | tuple, target_type: type | None = None,
              get_wrong_type: bool = False) -> bool | tuple[bool, type]:
    """
    Test whether all values in a list are of the same type.

    Args:
        lst (list | tuple): the list tested
        target_type (type | None): a specific type to test for the values
        get_wrong_type (bool): whether to return the type of the wrong value

    Returns:
        bool: test result
    """

    if target_type is None:
        target_type = type(lst[0])  # if all have same type as first, then all have same type

    for i in range(len(lst)):
        if type(lst[i]) is not target_type:
            if get_wrong_type:
                return False, type(lst[i])
            else:
                return False

    return True


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


def multi_bar(x: list | tuple | np.ndarray, y: list | tuple | np.ndarray, *args: Any,
              width: num_type = 0.8, show: bool = True, **kwargs: Any) -> None:
    """
    Plots a bar graph with multiple bars using given x y and parameters.

    Notes:
        Might raise error "TypeError: 'NoneType' object is not callable" when executing:
            plt.xticks(x_ticks, x)
        Possible solution: input x y as type np.ndarray, it seems to be a problem with the typing of
        the Debug function in Pycharm, doesn't raise error when executing using Run

    Args:
        x (list | tuple | np.ndarray): values for x-axis of the bar graph
        y (list | tuple | np.ndarray): values for corresponding values for y-axis
        *args (Any): any additional arguments to pass to plt.bar
        width (int | float): total width of the bars
        show (bool): whether to show the graph (user might need to add additional settings)
        **kwargs (Any): any additional keyword arguments to pass to plt.bar

    Raises:
        ValueError: unable to graph for 0 bars
    """

    # convert x and y to type np.ndarray
    if type_same(x, int):
        x = np.array(x, dtype=int)
    elif type_same(x, float):
        x = np.array(x, dtype=float)
    else:
        x = np.array(x, dtype=object)

    y = np.array(y, dtype=float)

    if 0 in y.shape:
        raise ValueError('unable to graph for 0 bars')

    bar_cnt = y.shape[0]
    w = width / bar_cnt

    # find the positions of the bars relative to the center of the bars
    rel_pos = (np.arange(bar_cnt) - (bar_cnt - 1) / 2) * w

    for i in range(bar_cnt):
        x_new = np.empty((len(x),), dtype=float)

        if x.dtype in decimal_dtype:
            x_new = x + rel_pos[i]
            x_ticks = copy.deepcopy(x)  # prevent changes to x_ticks and x from affecting each other

        # make the x positions 1 2 3 and so on if given x aren't numbers
        else:
            for j in range(len(x)):
                x_new[j] = j + 1 + rel_pos[i]
            x_ticks = np.arange(len(x)) + 1

        plt.bar(x_new, y[i], width=w, *args, **kwargs)

    # noinspection PyUnboundLocalVariable
    plt.xticks(x_ticks, x)

    if show:
        plt.show()


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


# noinspection PyUnusedLocal
def multi_array_index(arrs: list[np.ndarray] | tuple[np.ndarray] | dict[Any, np.ndarray],
                      index: list[int | Hashable]) -> list | dict:
    """
    Gets the items of each array at the given index.

    Args:
        arrs (list[np.ndarray] | dict[Any, np.ndarray]):
        index (list[int | Hashable]): the index of the arrs to get

    Returns:
        list | dict: the items at position index for each array
    """

    # use eval and string format list because length not known
    if type(arrs) in [list, tuple]:
        return [eval('arr' + str(list(index))) for arr in arrs]

    elif type(arrs) is dict:
        return {key: eval('arr[key]' + str(list(index))) for key in arrs.keys()}


# noinspection PyUnusedLocal
def apply_for_element(func: Any, arr: np.ndarray, *args,
                      dtype: np.dtype | None = None, **kwargs) -> np.ndarray:
    """
    Apply the given function to each element in the base array.

    Args:
        func (Any): the function to use
        arr (np.ndarray): the base array
        *args (): additional arguments, including other arrays to pass to function
        dtype (np.dtype): dtype of the return array
        **kwargs (): additional keyword arguments

    Returns:
        np.ndarray: the array after each element has been changed to function
    """
    # noinspection PyTypeChecker
    result_arr = np.empty(arr.shape, dtype=dtype)
    args = list(args)
    kwargs = list(kwargs)

    # broadcast to make sure every element gets the appropriate arguments
    for i in range(len(args)):
        args[i] = np.broadcast_to(args[i], arr.shape)

    for i in range(len(kwargs)):
        kwargs[i] = np.broadcast_to(kwargs[i], arr.shape)

    # select each element at a time, use multi_array_index for multiple arguments
    # use exec for indexing because length of arr.shape not known
    for i in itertools.product(*[list(range(i)) for i in arr.shape]):
        exec('result_arr{0} = func(arr[i], *multi_array_index(args,i), *multi_array_index(kwargs,'
             'i))'.format(str(list(i))))

    return result_arr


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


def list_concat(*lists: list) -> list:
    """
    Concatenates the lists.

    Args:
        *lists (list): the lists to concatenate

    Returns:
        list: concatenated list
    """
    result_list = []
    for i in lists:
        result_list = result_list + i

    return result_list
