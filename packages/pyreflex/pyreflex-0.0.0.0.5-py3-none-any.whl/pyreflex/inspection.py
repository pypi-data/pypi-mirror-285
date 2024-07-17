import inspect
import sys
from types import FrameType, MethodType


def stack(context = 1, *, depth = 1):
    """Return a list of records for the stack above the indicated depth caller's frame."""
    return inspect.getouterframes(sys._getframe(depth), context)


def get_frameinfo_at(depth = 1, context = 1):
    frame = sys._getframe(depth)
    frameinfo = (frame,) + inspect.getframeinfo(frame, context)
    return inspect.FrameInfo(*frameinfo)


def self_from_frame(frame: FrameType):
    '''
    Get the `self` instance of the frame if the frame is a called method, else `None` will be returned.
    '''
    co_varnames = frame.f_code.co_varnames
    if len(co_varnames) > 0:
        module_self = co_varnames[0]
        module_self = frame.f_locals[module_self]
        func_name = frame.f_code.co_name
        if hasattr(module_self, func_name) and frame.f_back.f_locals.get(func_name) is None:
            return module_self


def overriding_depth():
    frame = inspect.currentframe().f_back
    method_name = frame.f_code.co_name
    self = self_from_frame(frame)
    frame = frame.f_back
    i = 1
    while frame.f_code.co_name == method_name and self_from_frame(frame) is self:
        i += 1
        frame = frame.f_back
    return i