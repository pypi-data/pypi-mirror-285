from enum import Enum

__all__ = ["LocatorScope"]


class LocatorScope(Enum):
    Root = 0
    Descendants = 1
    Children = 2
    Parent = 3
    Ancestor = 4
    AncestorOrSelf = 5
    DescendantsOrSelf = 6
    Following = 7
    FollowingSibling = 8
    Preceding = 9
    PrecedingSibling = 10
