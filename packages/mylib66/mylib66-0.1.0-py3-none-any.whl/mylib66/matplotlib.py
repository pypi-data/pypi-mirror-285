# encoding: utf-8
from typing import *
import matplotlib.pyplot as plt
import numpy as np
from list import type_same
import copy

num_type = int | float

decimal_dtype = ['int32', 'int64', 'float32', 'float64']


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
