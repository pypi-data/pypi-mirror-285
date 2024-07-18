from abc import abstractmethod

from ...core.technology import Technology
from .devices.displaydevice import DisplayDevice
from .devices.keyboarddevice import KeyboardDevice
from .devices.mousedevice import MouseDevice
from .window_manager import WindowManager

__all__ = ["UiTechnology"]


class UiTechnology(Technology):
    @property
    @abstractmethod
    def mouse_device(self) -> MouseDevice:
        pass

    @property
    @abstractmethod
    def keyboard_device(self) -> KeyboardDevice:
        pass

    @property
    @abstractmethod
    def display_device(self) -> DisplayDevice:
        pass

    @property
    @abstractmethod
    def window_manager(self) -> WindowManager:
        pass
