from typing import Sequence, Optional, Any
import inspect
import sys
from types import FrameType


def stack(context = 1, *, depth = 0) -> Sequence[inspect.FrameInfo]:
    '''
    Return a list of records for the stack above the indicated depth caller's frame.
    '''
    return inspect.getouterframes(sys._getframe(depth + 1), context)


def get_frame_at(depth = 0) -> Optional[FrameType]:
    '''
    Return the frame at the given depth if accessible, otherwise return `None`.
    '''
    try:
        return sys._getframe(depth + 1)
    except ValueError:
        return None


def get_frameinfo_at(depth = 0, context = 1) -> Optional[inspect.FrameInfo]:
    '''
    Return the `FrameInfo` instance at the given depth if accessible, otherwise return `None`.
    '''
    frame = get_frame_at(depth)
    if frame:
        frameinfo = (frame,) + inspect.getframeinfo(frame, context)
        return inspect.FrameInfo(*frameinfo)


def self_from_frame(frame: FrameType) -> Any:
    '''
    Get the `self` instance of the frame if the frame is a called method, otherwise `None` will be returned.
    '''
    co_varnames = frame.f_code.co_varnames
    if len(co_varnames) > 0:
        module_self = co_varnames[0]
        module_self = frame.f_locals[module_self]
        func_name = frame.f_code.co_name
        if hasattr(module_self, func_name) and frame.f_back.f_locals.get(func_name) is None:
            return module_self


def overriding_depth() -> int:
    '''
    Used in the function that has been overriden by subclasses, with the current called overriding depth returned.
    '''
    frame = inspect.currentframe().f_back
    if frame:
        method_name = frame.f_code.co_name
        self = self_from_frame(frame)
        if self:
            frame = frame.f_back
            i = 1
            while frame and (frame.f_code.co_name == method_name and self_from_frame(frame) is self):
                i += 1
                frame = frame.f_back
            return i
    return 0