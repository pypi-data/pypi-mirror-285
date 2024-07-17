"""
函数工具
"""
import functools
from typing import Callable


def wrap_func(func: Callable, **kwargs):
    """包装函数，设置函数的某些参数值为固定的参数值"""
    return functools.partial(func, **kwargs)

