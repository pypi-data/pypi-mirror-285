from typing import cast

from PlatynUI.core import Adapter, StrategyImpl, strategy_impl_for
from PlatynUI.ui.strategies import (
    Control,
)

from ..technology import UiaTechnology
from ..uiabase import UiaBase

__all__ = ["ControlImpl"]


@strategy_impl_for(technology=UiaTechnology)
class ControlImpl(StrategyImpl, Control):
    def __init__(self, adapter: Adapter):
        self._adapter = adapter
        self._adapter
        self.element = cast(UiaBase, adapter).element

    @property
    def has_focus(self) -> bool:
        return bool(self.element.CurrentHasKeyboardFocus)

    def try_ensure_focused(self) -> bool:
        if self.has_focus:
            return True

        self.element.SetFocus()

        return self.has_focus
