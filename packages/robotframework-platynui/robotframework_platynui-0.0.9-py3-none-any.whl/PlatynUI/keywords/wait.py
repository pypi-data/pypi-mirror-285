from typing import Union

from robotlibcore import keyword

from ..technology.uiautomation import Locator
from ..ui import Element
from .types import TimeSpan

__all__ = ["Wait"]


class Wait:
    @keyword
    def ensure_exists(
        self, locator: Locator, timeout: Union[TimeSpan, float, None] = None, raise_exception: bool = True
    ) -> bool:
        element = Element(locator)
        return element.exists(
            timeout=timeout.seconds if isinstance(timeout, TimeSpan) else timeout, raise_exception=raise_exception
        )
