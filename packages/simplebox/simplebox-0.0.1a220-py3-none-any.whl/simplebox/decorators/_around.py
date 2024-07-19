#!/usr/bin/env python
# -*- coding:utf-8 -*-
from .._pypkg import Callable
from functools import wraps
from typing import TypeVar, Union

from ._hook import _run_hook_func
from ._process import _do
from ..generic import T

_TDict = TypeVar("_TDict", bound=dict)
_Types = Union[tuple[Callable], list[Callable], Callable, None]


def around(before: _Types = None, after: _Types = None, catch: bool = False) -> T:
    """
    Preform facet operations on functions
    It supports injecting the return value of the preceding hook function into the decorated function
    Support to inject the return value of the decorated function into the post hook function.

    The decorated function can get the return value of the fore hook function through the "func_return" parameter,
    and the after hook function can get the return value of the decorated function via the "func_return" parameter.

    All the parameters of the original function are injected into the hook function.

    :param catch: decorated function throw exception when runtime, if True, will catch exception and run hook function,
                    then throw origin exception. If False, throw the exception directly.
                    Valid only for after hook functions.
    :param before:
        Preceding hook function before the decorated function is executed.
        If "before" is a dictionary, the key is the hook function object,
        and the value is the parameter of the hook function.
        When the hook function is executed, it will be passed to the hook function in the form of key value pairs.
        If "before" is a list, it means that the hook function has no parameters.
        If "before" is an executable object, the hook function is directly executed
    :param after:
        Post hook function.
        reference resources @params before
    """
    def _inner(func):
        @wraps(func)
        def _wrapper(*args: tuple, **kwargs: dict):
            return _do(func=func, decorator_name=around.__name__, args=args, kwargs=kwargs,
                       opts={"before": before, "after": after, "catch": catch, "args": args, "kwargs": kwargs,
                             "stacklevel": 7})

        return _wrapper

    return _inner


def __do_around(func: Callable, args: tuple = None, kwargs: dict = None, opts: dict = None):
    args_ = args or ()
    kwargs_ = kwargs or {}
    result = None
    _run_hook_func(opts.get("before"), args, kwargs, opts.get("srcFuncClass", ""))
    # noinspection PyBroadException
    try:
        result = func(*args_, **kwargs_)
        return result
    except BaseException:
        if not opts.get("catch"):
            raise
    finally:
        kwargs["result"] = result
        _run_hook_func(opts.get("after"), args, kwargs, opts.get("srcFuncClass", ""))


__all__ = [around]
