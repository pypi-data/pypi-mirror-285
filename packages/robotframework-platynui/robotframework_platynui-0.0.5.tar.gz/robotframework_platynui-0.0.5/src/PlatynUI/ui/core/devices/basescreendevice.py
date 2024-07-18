from abc import ABC, abstractmethod

from ....core.types import Rect

__all__ = ["BaseScreenDevice"]


class BaseScreenDevice(ABC):
    @property
    @abstractmethod
    def rectangle(self) -> Rect:
        pass

    @abstractmethod
    def take_screen_shot(self, rect: Rect, filename: str, image_type: str) -> bool:
        pass
