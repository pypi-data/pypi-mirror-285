from ..core import context
from .element import *

__all__ = ["Graphic"]


@context
class Graphic(Element):
    pass


@context
class GraphicItem(Element):
    default_prefix = "item"
