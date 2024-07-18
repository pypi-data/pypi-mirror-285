from typing import Optional

from PlatynUI.ui.core.devices.basekeyboarddevice import BaseKeyboardDevice, BaseKeyCode, InputType, Key

from .loader import DotNetInterface


class UiaKeyboardDevice(BaseKeyboardDevice):
    def __init__(self) -> None:
        super().__init__()
        self.input_type: Optional[InputType] = None

    def key_to_keycode(self, key: Key) -> BaseKeyCode:
        result = DotNetInterface().keyboard_device().KeyToKeyCode(key)
        return BaseKeyCode(result.Key, result.Code, result.Valid, result.ErrorText)

    def send_keycode(self, keycode: BaseKeyCode, pressed: bool) -> bool:
        if not keycode.valid:
            raise ValueError(f"Invalid key: {keycode}")

        return DotNetInterface().keyboard_device().SendKeyCode(keycode.code, pressed)
