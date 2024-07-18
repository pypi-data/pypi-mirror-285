from PlatynUI.technology.uiautomation.locator import locator
from PlatynUI.ui import Button, Pane, Text, Window

# mypy: disable-error-code="empty-body"


@locator(name="Rechner")
class CalculatorWindow(Window):
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


calculator = CalculatorWindow()


@locator(name="Taskleiste")
class TaskbarPane(Pane):
    @property
    @locator(name="Start")
    def start(self) -> Button: ...


taskbar = TaskbarPane()

__all__ = ["calculator", "taskbar"]


if __name__ == "__main__":
    calculator.n0.activate()
