from typing import ClassVar, Optional

from ...core import Adapter, Point, Rect, StrategyBase

__all__ = ["Element", "TopLevelElement"]


class Element(StrategyBase):
    strategy_name: ClassVar[str] = "org.platynui.strategies.Element"

    @property
    def is_readonly(self) -> bool:
        raise NotImplementedError

    @property
    def is_enabled(self) -> bool:
        raise NotImplementedError

    @property
    def is_visible(self) -> bool:
        raise NotImplementedError

    @property
    def is_in_view(self) -> bool:
        raise NotImplementedError

    @property
    def toplevel_parent_is_active(self) -> bool:
        raise NotImplementedError

    @property
    def bounding_rectangle(self) -> Rect:
        raise NotImplementedError

    @property
    def visible_rectangle(self) -> Rect:
        raise NotImplementedError

    @property
    def top_level_parent(self) -> Optional[Adapter]:
        raise NotImplementedError

    @property
    def default_click_position(self) -> Point:
        raise NotImplementedError

    def try_ensure_visible(self) -> bool:
        raise NotImplementedError

    def try_ensure_application_is_ready(self) -> bool:
        raise NotImplementedError

    def try_ensure_toplevel_parent_is_active(self) -> bool:
        raise NotImplementedError

    def try_bring_into_view(self) -> bool:
        raise NotImplementedError


class TopLevelElement(StrategyBase):
    strategy_name = "org.platynui.strategies.TopLevelElement"

    @property
    def is_top_level_element(self) -> bool:
        raise NotImplementedError
