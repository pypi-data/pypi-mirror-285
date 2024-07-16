from typing import Union
import sys
import copy

def cast(value, *args, **kwargs):
    pass

def _blank_init(self, *args, **kwargs):
    pass

class initargs:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

def convert_to(type_target: type, value, inplace: bool, force_reinit: Union[bool, initargs]):
    original_type = value.__class__
    if not inplace:
        value = copy.copy(value)
    value.__class__ = type_target
    if isinstance(force_reinit, bool) and force_reinit:
        args = []
        kwargs = {}
    elif isinstance(force_reinit, initargs):
        args = force_reinit.args
        kwargs = force_reinit.kwargs
        force_reinit = True
    if force_reinit or (len(args) > 0) or (len(kwargs) > 0):
        if issubclass(type_target, original_type):
            original_type_init = original_type.__init__
            original_type.__init__ = _blank_init
            type_target.__init__(value, *args, **kwargs)
            original_type.__init__ = original_type_init
        else:
            type_target.__init__(value, *args, **kwargs)
    return value

def _get_converter_wrapper(type_target):
    def wrapper(value, inplace: bool = False, force_reinit: Union[bool, initargs] = False):
        return convert_to(type_target, value, inplace, force_reinit)
    return wrapper

if (sys.version_info.major, sys.version_info.minor) > (3, 7):
    class type_converter:
        @classmethod
        def __class_getitem__(cls, type_target):
            return _get_converter_wrapper(type_target)

    cast = type_converter
else:
    class type_converter:
        def __getitem__(self, type_target):
            return _get_converter_wrapper(type_target)

    cast = type_converter()