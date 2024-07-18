from ..core import context
from .control import Control

__all__ = ["Pane", "Group"]


@context
class Pane(Control):
    pass


@context
class Group(Control):
    pass
