from ..core import Point, Rect
from .core.devices import KeyboardDevice, MouseDevice
from .core.devices.keyboardproxy import KeyboardProxy
from .core.devices.mouseproxy import MouseProxy
from .element import Element

__all__ = ["DesktopBase"]


class DesktopBase(Element):
    default_role = "Desktop"

    class _DesktopMouseProxy(MouseProxy):
        def __init__(self, element: "DesktopBase", mouse_device: MouseDevice):
            super().__init__(mouse_device)
            self._element = element

        @property
        def base_point(self) -> Point:
            return self._element.bounding_rectangle.top_left

        @property
        def base_rect(self) -> Rect:
            return self._element.bounding_rectangle

        @property
        def default_click_position(self) -> Point:
            return self._element.default_click_position

        def before_action(self, action: MouseProxy.Action) -> None:
            self._element.ensure_that(self._element._adapter_exists)
            self.mouse_device.add_context(self._element)

        def after_action(self, action: MouseProxy.Action) -> None:
            self.mouse_device.remove_context(self._element)

    def _create_mouse_proxy(self, mouse_device: MouseDevice) -> MouseProxy:
        return self._DesktopMouseProxy(self, mouse_device)

    class _DesktopKeyboardProxy(KeyboardProxy):
        def __init__(self, element: "DesktopBase", keyboard_device: KeyboardDevice):
            super().__init__(keyboard_device)
            self._element = element

        def before_action(self, action: KeyboardProxy.Action) -> None:
            self._element.ensure_that(self._element._adapter_exists)
            self.keyboard_device.add_context(self._element)

        def after_action(self, action: KeyboardProxy.Action) -> None:
            self.keyboard_device.remove_context(self._element)

    def _create_keyboard_proxy(self, keyboard_device: KeyboardDevice) -> KeyboardProxy:
        return self._DesktopKeyboardProxy(self, keyboard_device)

    def _before_get_screenshot(self) -> None:
        pass
