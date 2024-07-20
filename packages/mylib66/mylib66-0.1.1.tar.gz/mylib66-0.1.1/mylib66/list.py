# encoding: utf-8
from typing import *


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
