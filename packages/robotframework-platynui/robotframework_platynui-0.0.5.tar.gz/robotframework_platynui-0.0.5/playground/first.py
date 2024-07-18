import time
from pathlib import Path
from typing import cast

from PlatynUI.core import Rect
from PlatynUI.core.adapter import Adapter
from PlatynUI.core.strategyimpl import StrategyImpl, strategy_impl_for
from PlatynUI.technology.uiautomation import Desktop, locator
from PlatynUI.technology.uiautomation.core.loader import DotNetInterface
from PlatynUI.technology.uiautomation.core.technology import UiaTechnology
from PlatynUI.technology.uiautomation.core.uiabase import UiaBase
from PlatynUI.ui import Application, Button, Group, Pane, Text, Window, strategies

# mypy: disable-error-code="empty-body"


@locator(name="Calc", use_default_prefix=True)
class MyApplication(Application):
    pass


@locator(name="Rechner")
class Calculator(Window):
    @property
    @locator(AutomationId="num0Button")
    def n0(self) -> Button: ...
    @property
    @locator(AutomationId="num1Button")
    def n1(self) -> Button: ...
    @property
    @locator(AutomationId="num2Button")
    def n2(self) -> Button: ...
    @property
    @locator(AutomationId="num3Button")
    def n3(self) -> Button: ...
    @property
    @locator(AutomationId="num4Button")
    def n4(self) -> Button: ...
    @property
    @locator(AutomationId="num5Button")
    def n5(self) -> Button: ...
    @property
    @locator(AutomationId="num6Button")
    def n6(self) -> Button: ...
    @property
    @locator(AutomationId="num7Button")
    def n7(self) -> Button: ...
    @property
    @locator(AutomationId="num8Button")
    def n8(self) -> Button: ...
    @property
    @locator(AutomationId="num9Button")
    def n9(self) -> Button: ...

    @property
    @locator(AutomationId="clearEntryButton")
    def clear_entry(self) -> Button: ...

    @property
    @locator(AutomationId="clearButton")
    def clear(self) -> Button: ...

    @property
    @locator(AutomationId="equalButton")
    def equal(self) -> Button: ...

    @property
    @locator(AutomationId="plusButton")
    def plus(self) -> Button: ...

    @property
    @locator(AutomationId="minusButton")
    def minus(self) -> Button: ...

    @property
    @locator(AutomationId="multiplyButton")
    def multiply(self) -> Button: ...

    @property
    @locator(AutomationId="divideButton")
    def divide(self) -> Button: ...

    @property
    @locator(AutomationId="NormalOutput")
    def results(self) -> Text: ...

    @property
    @locator(AutomationId="NumberPad")
    def number_pad(self) -> Group: ...


def test_seventh() -> None:
    calc = Calculator()

    print(calc.number_pad.bounding_rectangle)
    calc.number_pad.highlight()
    calc.number_pad.mouse.move_to(Rect.TOP_LEFT)
    calc.number_pad.mouse.move_to(Rect.BOTTOM_RIGHT)
    # calc.activate()
    # calc.highlight()

    for i in range(10):
        getattr(calc, f"n{i}").highlight()

    desktop = Desktop()
    desktop.mouse.move_to(x=calc.n1.bounding_rectangle.left, y=calc.n1.bounding_rectangle.top)
    desktop.mouse.move_to(x=calc.n2.bounding_rectangle.left, y=calc.n2.bounding_rectangle.top)
    desktop.mouse.move_to(x=calc.n3.bounding_rectangle.left, y=calc.n3.bounding_rectangle.top)

    desktop.mouse.move_to(calc.n4.bounding_rectangle.top_left)
    desktop.mouse.move_to(calc.n4.bounding_rectangle.top_right)
    desktop.mouse.move_to(calc.n4.bounding_rectangle.bottom_right)
    desktop.mouse.move_to(calc.n4.bounding_rectangle.bottom_left)

    calc.clear.activate()

    calc.n1.mouse.move_to()
    calc.n2.mouse.move_to()
    calc.n3.mouse.move_to()
    calc.n4.mouse.move_to()

    calc.clear.activate()
    calc.n1.activate()
    calc.n2.activate()
    calc.n3.activate()
    calc.n4.activate()
    calc.n5.activate()
    calc.n6.activate()
    calc.n7.activate()
    calc.n8.activate()
    calc.n9.activate()
    calc.n0.activate()

    # print(calc.results.text)
    calc.keyboard.type_keys("1234+12345+<Enter>")


# test_seventh()
# calc = Calculator()
# print(calc.locator.get_path(None, Calculator))

# myapp = MyApplication()
# print(myapp.locator.get_path(None, MyApplication))
# assert myapp.exists()


@strategy_impl_for(technology=UiaTechnology, class_name="Transparent Windows Client")
class TransparentWindowsClient(StrategyImpl, strategies.HasIsActive, strategies.Activatable, strategies.Control):
    def __init__(self, adapter: Adapter):
        self._adapter = adapter
        self._adapter
        self.element = cast(UiaBase, adapter).element
        self.window_pattern = DotNetInterface().patterns().GetNativeWindowPattern(self.element)

    @property
    def is_active(self) -> bool:
        return self.window_pattern.IsActive

    def activate(self) -> None:
        self.window_pattern.Activate()
        time.sleep(1)

    @property
    def has_focus(self) -> bool:
        return self.is_active

    def try_ensure_focused(self) -> bool:
        if self.has_focus:
            return True

        self.activate()

        return self.has_focus


@locator(name="Document1 - Word - \\\\Remote", class_name="Transparent Windows Client")
class WordCitrixWindow(Pane):
    default_role = "Pane"


@locator('ends-with(@Name, "- Word")', class_name="OpusApp")
class WordWindow(Window):
    pass


def citrix_test() -> None:
    w = WordCitrixWindow()
    # w = WordWindow()
    # w = Calculator()

    # w.focus()
    # w.mouse.click(Rect.TOP_RIGHT)

    w.keyboard.type_keys("Hallo Weltöäü🐑🤔")
    # w.keyboard.type_keys("<Alt+F4>")


# test_seventh()
# citrix_test()


def word_test() -> None:
    word = WordWindow()
    word.highlight()
    readme = Path(__file__).parent.parent / "README.md"
    readme_text = readme.read_text()
    word.keyboard.type_keys("Hallo Weltöäü🐑🤔")
    word.keyboard.type_keys(readme_text)


# word_test()


def highlight_test() -> None:
    word = WordWindow()
    word.focus()
    word.highlight()
    word.mouse.click()
    # for w in word.children:
    #     w.highlight()


# highlight_test()

calc = Calculator()
calc.clear.activate()
calc.n1.activate()
calc.n2.activate()


# @locator(name="Calculator", use_default_prefix=True)
# class CalcApp(Application):
#     @property
#     @locator()
#     def main_window(self) -> Calculator:
#         return Calculator()


# def calc_test() -> None:
#     calc = CalcApp()
#     calc.main_window.n1.activate()


# calc_test()
