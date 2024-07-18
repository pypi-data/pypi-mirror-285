from abc import *

from ...core import StrategyBase

__all__ = ["Text", "EditableText", "Clearable", "HasEditor", "HasMultiLine"]


class Text(StrategyBase):
    strategy_name = "org.platynui.strategies.Text"

    @property
    @abstractmethod
    def text(self) -> str:
        pass


class Clearable(StrategyBase):
    strategy_name = "org.platynui.strategies.Clearable"

    @abstractmethod
    def clear(self) -> None:
        pass


class EditableText(StrategyBase):
    strategy_name = "org.platynui.strategies.EditableText"

    @abstractmethod
    def set_text(self, value: str) -> None:
        pass


class HasEditor(StrategyBase):
    strategy_name = "org.platynui.strategies.HasEditor"

    @abstractmethod
    def open_editor(self):
        pass

    @abstractmethod
    def cancel(self):
        pass

    @abstractmethod
    def accept(self):
        pass


class HasMultiLine(StrategyBase):
    strategy_name = "org.platynui.strategies.HasMultiLine"

    @property
    @abstractmethod
    def is_multi_line(self) -> bool:
        pass
