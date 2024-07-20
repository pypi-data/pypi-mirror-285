# encoding: utf-8
import numpy as np
from typing import *
import itertools


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
