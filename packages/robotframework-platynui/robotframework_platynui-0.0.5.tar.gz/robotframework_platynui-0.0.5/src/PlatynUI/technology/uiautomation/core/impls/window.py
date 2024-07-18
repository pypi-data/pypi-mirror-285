from typing import cast

from PlatynUI.core import Adapter, StrategyImpl, strategy_impl_for
from PlatynUI.ui.strategies import (
    Activatable,
    Control,
    HasCanMaximize,
    HasCanMinimize,
    HasIsActive,
    Maximizable,
    Minimizable,
    Restorable,
)

from ..loader import DotNetInterface
from ..technology import UiaTechnology
from ..uiabase import UiaBase

__all__ = ["WindowPatternImpl"]


@strategy_impl_for(technology=UiaTechnology, properties={"IsWindowPatternAvailable": True})
@strategy_impl_for(technology=UiaTechnology, role="Window")
class WindowPatternImpl(
    StrategyImpl,
    Control,
    Minimizable,
    HasCanMinimize,
    HasCanMaximize,
    Maximizable,
    Restorable,
    HasIsActive,
    Activatable,
):
    def __init__(self, adapter: Adapter):
        self._adapter = adapter
        self._adapter
        self.element = cast(UiaBase, adapter).element
        self.window_pattern = DotNetInterface().patterns().GetWindowPattern(self.element)

    @property
    def has_focus(self) -> bool:
        return self.is_active

    def try_ensure_focused(self) -> bool:
        if self.has_focus:
            return True

        self.activate()

        return self.has_focus

    @property
    def can_minimize(self) -> bool:
        return self.window_pattern.CanMinimize

    @property
    def is_minimized(self) -> bool:
        return self.window_pattern.IsMinimized

    def minimize(self) -> None:
        self.window_pattern.Maximize()

    @property
    def can_maximize(self) -> bool:
        return self.window_pattern.CanMaximize

    @property
    def is_maximized(self) -> bool:
        return self.window_pattern.IsMaximized

    def maximize(self) -> None:
        self.window_pattern.Maximize()

    def restore(self) -> None:
        self.window_pattern.Restore()

    @property
    def is_active(self) -> bool:
        return self.window_pattern.IsActive

    def activate(self) -> None:
        self.window_pattern.Activate()
