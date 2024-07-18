from typing import Optional, cast

from ..core import ContextBase, ContextFactory, context
from ..core.exceptions import NoKeyboardProxyError, NoMouseProxyError
from ..core.predicate import predicate
from ..core.settings import Settings
from ..core.types import Point, Rect
from ..ui.core import UiTechnology
from ..ui.core.devices.displaydevice import DisplayDevice
from ..ui.core.devices.keyboarddevice import KeyboardDevice
from ..ui.core.devices.keyboardproxy import KeyboardProxy
from ..ui.core.devices.mousedevice import MouseDevice
from ..ui.core.devices.mouseproxy import MouseProxy
from . import strategies

__all__ = ["Element"]


@context
class Element(ContextBase):
    default_prefix = "element"

    def invalidate(self) -> None:
        super().invalidate()
        self._mouse_proxy = None
        self._keyboard_proxy = None

    @property
    def is_readonly(self) -> bool:
        self.ensure_that(self._application_is_ready)

        return self.adapter.get_strategy(strategies.Element).is_readonly

    @property
    def is_enabled(self) -> bool:
        self.ensure_that(self._application_is_ready)

        return self.adapter.get_strategy(strategies.Element).is_enabled

    @property
    def is_visible(self) -> bool:
        self.ensure_that(self._application_is_ready)

        return self.adapter.get_strategy(strategies.Element).is_visible

    @property
    def is_in_view(self) -> bool:
        self.ensure_that(self._application_is_ready)

        return self.adapter.get_strategy(strategies.Element).is_in_view

    @property
    def toplevel_parent_is_active(self) -> bool:
        from .window import Window

        self.ensure_that(self._application_is_ready)
        top_level_window = self.top_level_parent
        if isinstance(top_level_window, Window):
            return top_level_window.is_active

        return self.adapter.get_strategy(strategies.Element).toplevel_parent_is_active

    @property
    def bounding_rectangle(self) -> Rect:
        self.ensure_that(self._application_is_ready)

        return self.adapter.get_strategy(strategies.Element).bounding_rectangle

    @property
    def visible_rectangle(self) -> Rect:
        self.ensure_that(self._application_is_ready)

        return self.adapter.get_strategy(strategies.Element).visible_rectangle

    @property
    def default_click_position(self) -> Point:
        self.ensure_that(self._application_is_ready)

        return self.adapter.get_strategy(strategies.Element).default_click_position

    @predicate("element {0} is visible")
    def _element_is_visible(self) -> bool:
        self.ensure_that(self._application_is_ready)

        return self.adapter.get_strategy(strategies.Element).try_ensure_visible()

    @predicate("element {0} is enabled")
    def _element_is_enabled(self) -> bool:
        self.ensure_that(self._application_is_ready)

        return self.adapter.get_strategy(strategies.Element).is_enabled

    @predicate("element {0} is not readonly")
    def _element_is_not_readonly(self) -> bool:
        self.ensure_that(self._application_is_ready)

        return not self.adapter.get_strategy(strategies.Element).is_readonly

    @predicate("application for {0} is ready")
    def _application_is_ready(self) -> bool:
        if not self.is_valid:
            return True
        return self.adapter.get_strategy(strategies.Element).try_ensure_application_is_ready()

    def is_top_level_element(self) -> bool:
        strategy = self.adapter.get_strategy(strategies.TopLevelElement, False)
        if strategy is None:
            return False

        return strategy.is_top_level_element

    @property
    def top_level_parent(self) -> Optional["Element"]:
        self.ensure_that(self._adapter_exists)

        if not self.is_valid:
            return None

        parent = self.adapter.get_strategy(strategies.Element).top_level_parent
        if parent is None:
            return None

        loc = self.locator.create_top_level_locator(parent)
        if loc is None:
            return None

        result = loc.create_context(None, ContextFactory.find_context_class_for(parent))
        result.adapter = parent

        return result if isinstance(result, Element) else None

    @predicate("parent top level parent of element {0} is active")
    def _toplevel_parent_is_active(self) -> bool:
        self.ensure_that(self._application_is_ready)

        return self.adapter.get_strategy(strategies.Element).try_ensure_toplevel_parent_is_active()

    def activate_parent_window(self) -> bool:
        return self.ensure_that(self._toplevel_parent_is_active)

    @predicate("element {0} is in view")
    def _element_is_in_view(self) -> bool:
        self.ensure_that(self._element_is_visible)

        return self.adapter.get_strategy(strategies.Element).try_bring_into_view()

    def bring_to_view(self) -> bool:
        return self.ensure_that(self._toplevel_parent_is_active, self._element_is_in_view)

    def highlight(self, rect: Optional[Rect] = None, time: Optional[float] = None) -> None:
        if time is None:
            time = Settings.current().element_highlight_time
        if rect is None:
            rect = self.bounding_rectangle
        if self.is_visible:
            self.ensure_that(
                self._toplevel_parent_is_active,
                self._element_is_in_view,
                raise_exception=False,
                timeout=Settings.current().element_highlight_ensure_timeout,
            )

            if self.toplevel_parent_is_active and self.is_in_view:
                cast(UiTechnology, self.adapter.technology).display_device.highlight_rect(rect, time)

    class _ElementMouseProxy(MouseProxy):
        def __init__(self, element: "Element", mouse_device: MouseDevice):
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
            self._element.ensure_that(self._element._toplevel_parent_is_active, self._element._element_is_in_view)
            self.mouse_device.add_context(self._element)

        def after_action(self, action: MouseProxy.Action) -> None:
            self.mouse_device.remove_context(self._element)
            self._element.ensure_that(self._element._application_is_ready, raise_exception=False)

    _mouse_proxy: Optional[MouseProxy] = None

    def _create_mouse_proxy(self, mouse_device: MouseDevice) -> MouseProxy:
        return self._ElementMouseProxy(self, mouse_device)

    @property
    def mouse(self) -> MouseProxy:
        if self._mouse_proxy is None:
            self._mouse_proxy = self._create_mouse_proxy(cast(UiTechnology, self.adapter.technology).mouse_device)

        if self._mouse_proxy is None:
            raise NoMouseProxyError("cannot get a valid mouse device")

        return self._mouse_proxy

    class _ElementKeyboardProxy(KeyboardProxy):
        def __init__(self, element: "Element", keyboard_device: KeyboardDevice):
            super().__init__(keyboard_device)
            self._element = element

        def before_action(self, action: KeyboardProxy.Action) -> None:
            self._element.ensure_that(
                self._element._toplevel_parent_is_active,
                self._element._element_is_visible,
                self._element._element_is_in_view,
            )
            self.keyboard_device.add_context(self._element)

        def after_action(self, action: KeyboardProxy.Action) -> None:
            self.keyboard_device.remove_context(self._element)
            self._element.ensure_that(self._element._application_is_ready, raise_exception=False)

    _keyboard_proxy: Optional[KeyboardProxy] = None

    def _create_keyboard_proxy(self, keyboard_device: KeyboardDevice) -> KeyboardProxy:
        return self._ElementKeyboardProxy(self, keyboard_device)

    @property
    def keyboard(self) -> KeyboardProxy:
        if self._keyboard_proxy is None:
            self._keyboard_proxy = self._create_keyboard_proxy(
                cast(UiTechnology, self.adapter.technology).keyboard_device
            )

        if self._keyboard_proxy is None:
            raise NoKeyboardProxyError("cannot get a valid keyboard device")

        return self._keyboard_proxy

    @property
    def display(self) -> DisplayDevice:
        return cast(UiTechnology, self.adapter.technology).display_device

    def _before_get_screenshot(self) -> None:
        self.ensure_that(self._toplevel_parent_is_active, self._element_is_in_view)

    def get_screenshot(
        self, rect: Optional[Rect] = None, format: Optional[str] = None, quality: Optional[int] = None
    ) -> bytearray:
        self._before_get_screenshot()

        return self.display.get_screenshot(rect if rect is not None else self.bounding_rectangle, format, quality)

    def save_screenshot(
        self,
        filename: Optional[str] = None,
        rect: Optional[Rect] = None,
        format: Optional[str] = None,
        quality: Optional[int] = None,
    ) -> str:
        self._before_get_screenshot()

        return self.display.save_screenshot(
            filename, rect if rect is not None else self.bounding_rectangle, format, quality
        )
