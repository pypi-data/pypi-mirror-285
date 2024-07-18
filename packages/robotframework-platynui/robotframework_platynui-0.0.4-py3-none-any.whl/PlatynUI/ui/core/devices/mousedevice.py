import abc
import time
from typing import Any, Iterator, Optional

from ....core.settings import Settings
from ....core.types import Point, Rect
from ....robot.reporting import report_as_keyword
from .basemousedevice import BaseMouseDevice
from .inputdevice import InputDevice
from .mousebutton import MouseButton

__all__ = ["MouseDevice", "DefaultMouseDevice"]


class MouseDevice(InputDevice):
    __double_click_time: float = 0.4
    __multi_click_delay: Optional[float] = None
    __press_release_delay: Optional[float] = None
    __after_move_delay: Optional[float] = None
    __move_delay: Optional[float] = None
    __move_time: Optional[float] = None
    __after_click_delay: Optional[float] = None
    __before_next_click_delay: Optional[float] = None

    default_button = MouseButton.left

    @property
    def double_click_time(self) -> float:
        return self.__double_click_time

    @double_click_time.setter
    def double_click_time(self, value: float) -> None:
        self.__double_click_time = value

    @property
    def before_next_click_delay(self) -> float:
        if self.__before_next_click_delay is None:
            return self.double_click_time * Settings.current().mouse_before_next_click_delay_multiplicator
        return self.__before_next_click_delay

    @before_next_click_delay.setter
    def before_next_click_delay(self, value: Optional[float]) -> None:
        self.__before_next_click_delay = value

    @property
    def after_click_delay(self) -> float:
        if self.__after_click_delay is None:
            return Settings.current().mouse_after_click_delay
        return self.__after_click_delay

    @after_click_delay.setter
    def after_click_delay(self, value: Optional[float]) -> None:
        self.__after_click_delay = value

    @property
    def multi_click_delay(self) -> float:
        if self.__multi_click_delay is None:
            return self.double_click_time * Settings.current().mouse_multi_click_delay_multiplicator
        return self.__multi_click_delay

    @multi_click_delay.setter
    def multi_click_delay(self, value: Optional[float]) -> None:
        self.__multi_click_delay = value

    @property
    def press_release_delay(self) -> float:
        if self.__press_release_delay is None:
            return Settings.current().mouse_press_release_delay
        return self.__press_release_delay

    @press_release_delay.setter
    def press_release_delay(self, value: Optional[float]) -> None:
        self.__press_release_delay = value

    @property
    def after_move_delay(self) -> float:
        if self.__after_move_delay is None:
            return Settings.current().mouse_after_move_delay
        return self.__after_move_delay

    @after_move_delay.setter
    def after_move_delay(self, value: Optional[float]) -> None:
        self.__move_time = value

    @property
    def move_time(self) -> float:
        if self.__move_time is None:
            return Settings.current().mouse_move_time
        return self.__move_time

    @move_time.setter
    def move_time(self, value: Optional[float]) -> None:
        self.__move_time = value

    @property
    def move_delay(self) -> float:
        if self.__move_delay is None:
            return Settings.current().mouse_move_delay
        return self.__move_delay

    @move_delay.setter
    def move_delay(self, value: Optional[float]) -> None:
        self.__move_delay = value

    def add_context(self, context: Any) -> None:
        pass

    def remove_context(self, context: Any) -> None:
        pass

    @abc.abstractmethod
    def get_position(self) -> Point:
        pass

    @abc.abstractmethod
    def move_to(
        self, pos: Point = None, x: Optional[float] = None, y: Optional[float] = None, raise_exception: bool = True
    ) -> Optional[Point]:
        pass

    @abc.abstractmethod
    def press(
        self, pos: Point = None, x: Optional[float] = None, y: Optional[float] = None, button: MouseButton = None
    ) -> Optional[Point]:
        pass

    @abc.abstractmethod
    def release(
        self, pos: Point = None, x: Optional[float] = None, y: Optional[float] = None, button: MouseButton = None
    ) -> Optional[Point]:
        pass

    @abc.abstractmethod
    def click(
        self,
        pos: Point = Point(),
        x: Optional[float] = None,
        y: Optional[float] = None,
        button: MouseButton = None,
        times: int = 1,
    ) -> Optional[Point]:
        pass


class DefaultMouseDevice(MouseDevice):
    __base_mouse_device = None  # type: BaseMouseDevice

    def __init__(self, base_mouse_device: BaseMouseDevice):
        self.__base_mouse_device = base_mouse_device
        self.double_click_time = self.__base_mouse_device.double_click_time

    @property
    def base_mouse_device(self) -> BaseMouseDevice:
        return self.__base_mouse_device

    def get_position(self) -> Point:
        return self.__base_mouse_device.get_position()

    def _generate_move_events(self, start_pos: Point, end_pos: Point) -> Iterator[Point]:
        start_time = time.monotonic()
        end_time = start_time + self.move_time

        while True:
            current_time = end_time - time.monotonic()
            if current_time > 0:
                step = current_time / self.move_time

                yield Point((1 - step) * end_pos.x + step * start_pos.x, (1 - step) * end_pos.y + step * start_pos.y)
            else:
                break

    @report_as_keyword
    def move_to(
        self, pos: Point = None, x: Optional[float] = None, y: Optional[float] = None, raise_exception: bool = True
    ) -> Point:
        if pos is None:
            pos = Point()

        start_pos = self.get_position()
        if not pos:
            pos = start_pos.clone()

        if x is not None:
            pos.x = x
        if y is not None:
            pos.y = y

        if pos and pos != start_pos:
            if self.move_time > 0 and self.move_delay < self.move_time:
                for p in self._generate_move_events(start_pos, pos):
                    self.__base_mouse_device.move_to(p)
                    self.delay(self.move_delay)

            self.__base_mouse_device.move_to(pos)

            self.delay(self.after_move_delay)
            self.delay(self.after_input_delay)
        else:
            if not pos and raise_exception:
                raise Exception("invalid position %s" % pos)

        return pos

    @report_as_keyword
    def press(
        self, pos: Point = None, x: Optional[float] = None, y: Optional[float] = None, button: MouseButton = None
    ) -> Optional[Point]:
        if button is None:
            button = self.default_button

        result = self.move_to(pos=pos, x=x, y=y, raise_exception=False)

        self.__base_mouse_device.press(button)

        self.delay(self.press_release_delay)
        self.delay(self.after_input_delay)

        return result

    @report_as_keyword
    def release(
        self, pos: Point = None, x: Optional[float] = None, y: Optional[float] = None, button: MouseButton = None
    ) -> Optional[Point]:
        if button is None:
            button = self.default_button

        result = self.move_to(pos=pos, x=x, y=y, raise_exception=False)

        self.__base_mouse_device.release(button)

        self.delay(self.press_release_delay)
        self.delay(self.after_input_delay)

        return result

    _last_click_time: float = 0
    _last_click_pos: Point = Point()
    _last_click_rect = Rect()

    def _calc_last_click_rect(self, p: Point) -> Rect:
        size = self.__base_mouse_device.double_click_size

        return Rect(p.x - size.width / 2, p.y - size.height / 2, size.width, size.height)

    @report_as_keyword
    def click(
        self,
        pos: Point = Point(),
        x: Optional[float] = None,
        y: Optional[float] = None,
        button: Optional[MouseButton] = None,
        times: int = 1,
    ) -> Optional[Point]:
        last_click_time_span = time.time() - self._last_click_time

        if button is None:
            button = self.default_button

        result = self.move_to(pos=pos, x=x, y=y, raise_exception=False)

        if self._last_click_rect.contains(result) and last_click_time_span < self.before_next_click_delay:
            self.delay(self.before_next_click_delay - last_click_time_span)

        for i in range(times):
            if i > 0:
                self.delay(self.multi_click_delay)

            self.__base_mouse_device.press(button)
            self.delay(self.press_release_delay)
            self.__base_mouse_device.release(button)

        self._last_click_time = time.time()
        self._last_click_pos = result
        self._last_click_rect = self._calc_last_click_rect(result)

        self.delay(self.after_click_delay)
        self.delay(self.after_input_delay)

        return result
