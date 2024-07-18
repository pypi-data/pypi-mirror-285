from abc import abstractmethod

from ...core import StrategyBase
from ...core.types import Point, Size

__all__ = ["WindowManager"]


class WindowManager(StrategyBase):
    strategy_name = "org.platynui.WindowManager"

    @property
    @abstractmethod
    def window_manager_present(self) -> bool:
        pass

    @property
    @abstractmethod
    def window_manager_name(self) -> str:
        pass

    @property
    @abstractmethod
    def root_window_id(self) -> bytes:
        pass

    @property
    @abstractmethod
    def active_window(self) -> bytes:
        pass

    @abstractmethod
    def activate_window(self, id: bytes) -> None:
        pass

    @abstractmethod
    def maximize_window(self, id: bytes) -> None:
        pass

    @abstractmethod
    def minimize_window(self, id: bytes) -> None:
        pass

    @abstractmethod
    def restore_window(self, id: bytes) -> None:
        pass

    @abstractmethod
    def close_window(self, id: bytes) -> None:
        pass

    @abstractmethod
    def move_window(self, id: bytes, pos: Point) -> None:
        pass

    @abstractmethod
    def resize_window(self, id: bytes, size: Size) -> None:
        pass
