from ..core import context
from . import strategies
from .control import Control
from .togglestate import ToggleState

__all__ = ["AbstractButton", "Button", "Link", "ToggleState", "CheckBox", "RadioButton"]


class AbstractButton(Control):
    @property
    def text(self) -> str:
        self.ensure_that(self._application_is_ready)

        return self.adapter.get_strategy(strategies.Text).text


@context
class Button(AbstractButton, strategies.Activatable):
    def activate(self) -> None:
        self.ensure_that(self._toplevel_parent_is_active, self._element_is_in_view, self._element_is_enabled)

        self.adapter.get_strategy(strategies.Activatable).activate()

        self.ensure_that(self._application_is_ready, raise_exception=False)


@context
class Link(Button):
    pass


@context
class CheckBox(AbstractButton):
    @property
    def state(self) -> ToggleState:
        self.ensure_that(self._application_is_ready)

        return self.adapter.get_strategy(strategies.HasToggleState).state

    @state.setter
    def state(self, value: ToggleState) -> None:
        self.set_state(value)

    def set_state(self, state: ToggleState) -> None:
        for _ in ToggleState:
            if self.state == state:
                break
            self.toggle()

    def activate(self) -> None:
        self.set_state(ToggleState.Checked)

    def check(self) -> None:
        self.set_state(ToggleState.Checked)

    @property
    def is_checked(self) -> bool:
        return self.state == ToggleState.Checked

    @property
    def is_unchecked(self) -> bool:
        return self.state == ToggleState.Unchecked

    def uncheck(self) -> None:
        self.set_state(ToggleState.Unchecked)

    def toggle(self) -> None:
        self.ensure_that(
            self._toplevel_parent_is_active,
            self._element_is_in_view,
            self._element_is_enabled,
            self._element_is_not_readonly,
        )

        self.adapter.get_strategy(strategies.Toggleable).toggle()

        self.ensure_that(self._application_is_ready, raise_exception=False)


@context
class RadioButton(AbstractButton):
    pass
