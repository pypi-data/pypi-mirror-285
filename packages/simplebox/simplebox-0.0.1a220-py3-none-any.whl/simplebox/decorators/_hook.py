#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
from collections.abc import Iterable
from inspect import getfullargspec

from ._tools import AstTools
from .._pypkg import Callable


def _run_hook_func(call_obj: Iterable[Callable] or Callable, args: tuple, kwargs: dict,
                   src_func_class: str = "") -> dict:
    if not call_obj:
        return {}
    call_list = []
    if issubclass(type(call_obj), Iterable):
        call_list.extend(call_obj)
    else:
        call_list.append(call_obj)
    for call in call_list:
        call_type_name = type(call).__name__
        hook_args = []
        hook_kwargs = {}
        if call_type_name == "function":
            assert callable(call), f"'{call_type_name}' not a callable"
            __hook_params(call, hook_args, hook_kwargs, args, kwargs, src_func_class)
            call(*hook_args, **hook_kwargs)
        elif call_type_name == "method":
            assert callable(call), f"'{call_type_name}' not a callable"
            __hook_params(call, hook_args, hook_kwargs, args, kwargs, src_func_class)
            call(*hook_args, **hook_kwargs)
        else:
            assert hasattr(call, "__func__"), f"'{call_type_name}' not a callable"
            __hook_params(call.__func__, hook_args, hook_kwargs, args, kwargs, src_func_class)
            call.__func__(*hook_args, **hook_kwargs)


def __hook_params(call, hook_args: list, hook_kwargs: dict, args: tuple, kwargs: dict, src_func_class: str = ""):
    call_spec = getfullargspec(call)
    if not call_spec.args and call_spec.varargs:
        hook_args.extend(args)
    elif not call_spec.args and not call_spec.varargs:
        pass
    elif call_spec:
        func_full_name: str = call.__qualname__
        module = sys.modules[call.__module__]
        if isinstance(t := args[0], type):
            type_ = t
        else:
            type_ = type(t)
        if "." in func_full_name:
            if "." in str(src_func_class):
                class_name = func_full_name.split(".")[0]
                clz = getattr(module, class_name, None)
                decorator_name_list = AstTools(clz).get_decorator_of_function_by_name(call.__name__)
                if decorator_name_list and "staticmethod" in decorator_name_list:
                    if type_ == src_func_class:
                        hook_args.extend(args[1:])
                    else:
                        hook_args.extend(args)
                else:
                    if type_ == clz:
                        hook_args.extend(args)
                    else:
                        hook_args.extend(args[1:])
            else:
                hook_args.extend(args)
        else:
            if type_ == src_func_class:
                hook_args.extend(args[1:])
            else:
                hook_args.extend(args)

    if not call_spec.varkw and not call_spec.kwonlyargs:
        return
    hook_kwargs.update(kwargs)