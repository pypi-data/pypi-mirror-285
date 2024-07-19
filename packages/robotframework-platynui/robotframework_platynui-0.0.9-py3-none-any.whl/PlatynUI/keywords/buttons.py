from robotlibcore import keyword

from ..core.contextbase import ContextBase
from ..ui.strategies import Activatable

__all__ = ["Buttons"]


class Buttons:
    @keyword
    def activate(self, element: Activatable) -> None:
        element.activate()

    @keyword
    def click(self, locator: ContextBase) -> None:
        locator.mouse.click()
