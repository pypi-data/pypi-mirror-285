from abc import abstractmethod

from ...core import StrategyBase

__all__ = ["Application"]


class Application(StrategyBase):
    strategy_name = "org.platynui.strategies.Application"

    @property
    @abstractmethod
    def application_name(self) -> str:
        pass

    @property
    @abstractmethod
    def process_id(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @abstractmethod
    def exit(self) -> None:
        pass
