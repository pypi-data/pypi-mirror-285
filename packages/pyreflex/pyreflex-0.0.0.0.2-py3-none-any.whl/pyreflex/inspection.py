import inspect
import sys

def stack(context = 1, *, depth = 1):
    """Return a list of records for the stack above the indicated depth caller's frame."""
    return inspect.getouterframes(sys._getframe(depth), context)