from ...core import context
from ...ui.desktopbase import DesktopBase
from .locator import locator

__all__ = ["Desktop"]


@locator(path="/.")
@context
class Desktop(DesktopBase):
    pass
