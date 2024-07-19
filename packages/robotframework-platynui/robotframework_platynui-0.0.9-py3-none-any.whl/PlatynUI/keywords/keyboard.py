from typing import Optional

from robotlibcore import keyword

from ..ui import Element


class Keyboard:
    @keyword
    def type_keys(self, element: Element, *keys: str, delay: Optional[float] = None) -> None:
        element.keyboard.type_keys(*keys, delay=delay)

    @keyword
    def press_keys(self, element: Element, *keys: str, delay: Optional[float] = None) -> None:
        element.keyboard.press_keys(*keys, delay=delay)

    @keyword
    def release_keys(self, element: Element, *keys: str, delay: Optional[float] = None) -> None:
        element.keyboard.release_keys(*keys, delay=delay)
