from abc import *

from ...core import StrategyBase

__all__ = ["HasNativeWindowHandle"]


class HasNativeWindowHandle(StrategyBase):
    strategy_name = "org.platynui.strategies.HasNativeWindowHandle"

    @property
    @abstractmethod
    def native_window_handle(self) -> bytes:
        pass
