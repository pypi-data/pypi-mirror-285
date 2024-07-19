from ..core import context
from ..core.predicate import predicate
from . import strategies
from .core.devices.keyboarddevice import KeyboardDevice
from .core.devices.keyboardproxy import KeyboardProxy
from .element import Element

__all__ = ["Control", "CustomControl"]


@context
class Control(Element):
    default_role = "Control"

    @property
    def has_focus(self) -> bool:
        self.ensure_that(self._application_is_ready)

        return self.adapter.get_strategy(strategies.Control).has_focus

    @predicate("control {0} has focus")
    def _control_has_focus(self) -> bool:
        self.ensure_that(self._toplevel_parent_is_active, self._element_is_in_view)

        return self.adapter.get_strategy(strategies.Control).try_ensure_focused()

    def focus(self) -> bool:
        return self.ensure_that(self._control_has_focus)

    class _ControlKeyboardProxy(KeyboardProxy):
        def __init__(self, control: "Control", keyboard_device: KeyboardDevice):
            super().__init__(keyboard_device)
            self._control = control

        def before_action(self, action: KeyboardProxy.Action) -> None:
            self._control.ensure_that(self._control._control_has_focus)
            self.keyboard_device.add_context(self._control)

        def after_action(self, action: KeyboardProxy.Action) -> None:
            self._control.ensure_that(self._control._application_is_ready, raise_exception=False)
            self.keyboard_device.remove_context(self._control)

    def _create_keyboard_proxy(self, keyboard_device: KeyboardDevice) -> KeyboardProxy:
        return self._ControlKeyboardProxy(self, keyboard_device)


@context
class CustomControl(Element):
    default_role = "*"
