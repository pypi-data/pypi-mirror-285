from robotlibcore import keyword

from ..ui import Element


class Mouse:
    @keyword
    def mouse_click(self, locator: Element, text: str) -> None:
        raise NotImplementedError
