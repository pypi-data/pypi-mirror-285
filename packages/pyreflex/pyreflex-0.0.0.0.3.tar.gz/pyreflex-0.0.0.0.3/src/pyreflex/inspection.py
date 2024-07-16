import inspect
import sys


def stack(context = 1, *, depth = 1):
    """Return a list of records for the stack above the indicated depth caller's frame."""
    return inspect.getouterframes(sys._getframe(depth), context)


def get_frameinfo_at(depth = 1, context = 1):
    frame = sys._getframe(depth)
    frameinfo = (frame,) + inspect.getframeinfo(frame, context)
    return inspect.FrameInfo(*frameinfo)