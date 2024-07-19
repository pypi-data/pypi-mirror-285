from robotlibcore import keyword

from ..core.contextbase import ContextBase


class Application:
    @keyword
    def start_application(self, locator: ContextBase) -> None:
        raise NotImplementedError

    def close_application(self, locator: ContextBase) -> None:
        raise NotImplementedError

    def exit_application(self, locator: ContextBase) -> None:
        raise NotImplementedError

    def switch_to_application(self, locator: ContextBase) -> None:
        raise NotImplementedError
