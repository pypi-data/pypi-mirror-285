from abc import ABC
from typing import ClassVar, Optional

__all__ = ["StrategyBase"]


class StrategyBase(ABC):
    strategy_name: ClassVar[Optional[str]] = None
