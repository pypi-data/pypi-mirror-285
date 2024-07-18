import enum
from abc import ABCMeta, abstractmethod
from typing import Any, Optional, cast

from ....core import Adapter, InvalidArgumentError
from ....core.types import Point, Rect, VirtualPoint
from ... import strategies
from ..ui_technology import UiTechnology
from .mousebutton import MouseButton
from .mousedevice import MouseDevice

__all__ = ["MouseProxy", "MouseButton", "AdapterMouseProxy"]


class MouseProxy(metaclass=ABCMeta):
    def __init__(self, mouse_device: MouseDevice):
        self._mouse_device = mouse_device

    def __enter__(self) -> "MouseProxy":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass

    @property
    def mouse_device(self) -> MouseDevice:
        return self._mouse_device

    @property
    @abstractmethod
    def base_point(self) -> Point: ...

    @property
    @abstractmethod
    def base_rect(self) -> Rect: ...

    @property
    def default_click_position(self) -> Point:
        return Point(0, 0)

    class Action(enum.Enum):
        MOVE = 1
        PRESS = 2
        RELEASE = 3
        CLICK = 4
        DOUBLE_CLICK = 6

    def before_action(self, action: Action) -> None:
        pass

    def after_action(self, action: Action) -> None:
        pass

    def _calc_mouse_point(
        self, pos: Optional[Point] = None, x: Optional[float] = None, y: Optional[float] = None
    ) -> Point:
        if pos is None:
            pos = Point()
        if not isinstance(pos, Point):
            raise InvalidArgumentError("pos must be of type Point")

        if isinstance(pos, VirtualPoint):
            default = pos.calc_rect(self.base_rect)
            base = self._mouse_device.get_position()
            if not default.x_is_valid():
                default.x = base.x
            if not default.y_is_valid():
                default.y = base.y
            pos = Point(default.x if x is None else base.x, default.y if y is None else base.y)
        elif not pos:
            default = self.default_click_position
            base = self.base_point
            pos.x = default.x if x is None else base.x
            pos.y = default.y if y is None else base.y
        else:
            pos = self.base_point + pos if self.base_point is not None else pos

        if x is not None:
            pos.x += x

        if y is not None:
            pos.y += y

        return pos

    def move_to(self, pos: Point = None, x: Optional[float] = None, y: Optional[float] = None) -> Optional[Point]:
        self.before_action(MouseProxy.Action.MOVE)

        result = self.mouse_device.move_to(self._calc_mouse_point(pos, x, y))

        self.after_action(MouseProxy.Action.MOVE)

        return result

    def press(
        self,
        pos: Point = None,
        x: Optional[float] = None,
        y: Optional[float] = None,
        button: Optional[MouseButton] = None,
    ) -> Optional[Point]:
        self.before_action(MouseProxy.Action.PRESS)

        result = self.mouse_device.press(self._calc_mouse_point(pos, x, y), button=button)

        self.after_action(MouseProxy.Action.PRESS)

        return result

    def release(
        self,
        pos: Point = None,
        x: Optional[float] = None,
        y: Optional[float] = None,
        button: Optional[MouseButton] = None,
    ) -> Optional[Point]:
        self.before_action(MouseProxy.Action.RELEASE)

        result = self.mouse_device.release(self._calc_mouse_point(pos, x, y), button=button)

        self.after_action(MouseProxy.Action.RELEASE)

        return result

    def click(
        self,
        pos: Point = None,
        x: Optional[float] = None,
        y: Optional[float] = None,
        button: Optional[MouseButton] = None,
        times: int = 1,
    ) -> Optional[Point]:
        self.before_action(MouseProxy.Action.CLICK)

        result = self.mouse_device.click(self._calc_mouse_point(pos, x, y), button=button, times=times)

        self.after_action(MouseProxy.Action.CLICK)

        return result

    def double_click(
        self,
        pos: Point = None,
        x: Optional[float] = None,
        y: Optional[float] = None,
        button: Optional[MouseButton] = None,
    ) -> Optional[Point]:
        self.before_action(MouseProxy.Action.DOUBLE_CLICK)

        result = self.click(pos, x, y, button, 2)

        self.after_action(MouseProxy.Action.DOUBLE_CLICK)

        return result


class AdapterMouseProxy(MouseProxy):
    def __init__(self, adapter: Adapter, mouse_device: MouseDevice = None):
        super().__init__(mouse_device or cast(UiTechnology, adapter.technology).mouse_device)
        self._adapter = adapter

    @property
    def base_point(self) -> Point:
        return self._adapter.get_strategy(strategies.Element).bounding_rectangle.top_left

    @property
    def base_rect(self) -> Rect:
        return self._adapter.get_strategy(strategies.Element).bounding_rectangle

    @property
    def default_click_position(self) -> Point:
        return self._adapter.get_strategy(strategies.Element).default_click_position

    def before_action(self, action: MouseProxy.Action) -> None:
        self.mouse_device.add_context(self._adapter)

    def after_action(self, action: MouseProxy.Action) -> None:
        self.mouse_device.remove_context(self._adapter)
