import threading
from functools import cached_property
from typing import Optional

from PlatynUI.core import AdapterFactory
from PlatynUI.ui.core import UiTechnology, WindowManager
from PlatynUI.ui.core.devices import (
    DefaultDisplayDevice,
    DefaultKeyboardDevice,
    DefaultMouseDevice,
    DisplayDevice,
    KeyboardDevice,
    MouseDevice,
)

__all__ = ["UiaTechnology", "get_technology"]


class UiaTechnology(UiTechnology):
    def __init__(self) -> None:
        super().__init__()

    @cached_property
    def adapter_factory(self) -> AdapterFactory:
        from .adapterfactory import UiaAdapterFactory

        return UiaAdapterFactory(self)

    @cached_property
    def mouse_device(self) -> MouseDevice:
        from .mousedevice import UiaMouseDevice

        return DefaultMouseDevice(UiaMouseDevice())

    @property
    def keyboard_device(self) -> KeyboardDevice:
        from .keyboarddevice import UiaKeyboardDevice

        return DefaultKeyboardDevice(UiaKeyboardDevice())

    @property
    def display_device(self) -> DisplayDevice:
        from .displaydevice import UiaDisplayDevice

        return DefaultDisplayDevice(UiaDisplayDevice())

    @property
    def window_manager(self) -> WindowManager:
        raise NotImplementedError


__instance: Optional[UiaTechnology] = None
__lock = threading.Lock()


def get_technology() -> UiaTechnology:
    global __instance
    with __lock:
        if __instance is None:
            __instance = UiaTechnology()
        return __instance
