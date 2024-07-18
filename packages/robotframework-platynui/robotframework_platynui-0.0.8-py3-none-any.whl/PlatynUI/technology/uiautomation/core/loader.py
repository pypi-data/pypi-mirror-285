import logging
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Optional, cast

__all__ = ["DotNetInterface"]

logger = logging.getLogger(__name__)

# pyright: reportMissingModuleSource=false

if TYPE_CHECKING:
    from PlatynUI.Technology.UiAutomation import (
        Adapter,
        DisplayDevice,
        Finder,
        KeyboardDevice,
        MouseDevice,
        Patterns,
    )


class DotNetInterface:
    _adapter: Optional["Adapter"] = None
    _finder: Optional["Finder"] = None
    _mouse_device: Optional["MouseDevice"] = None
    _keyboard_device: Optional["KeyboardDevice"] = None
    _display_device: Optional["DisplayDevice"] = None
    _patterns: Optional["Patterns"] = None

    __loaded = False

    @classmethod
    def _ensure_loaded(cls) -> None:
        if cls.__loaded:
            return

        cls.__loaded = True

        import clr
        from pythonnet import get_runtime_info

        rt_kind = get_runtime_info().kind
        logger.debug(f"Runtime kind: {rt_kind}")  # noqa: G004

        if rt_kind == "CoreCLR":
            kind = "coreclr"
        elif rt_kind == ".NET Framework":
            kind = "netfx"
        else:
            logger.error(f"Unsupported runtime for PlatynUI: {get_runtime_info().kind}")  # noqa: G004
            raise RuntimeError(f"Unsupported runtime for PlatynUI: {get_runtime_info().kind}")

        logger.debug(f"Runtime kind: {rt_kind}")  # noqa: G004

        assembly_name = "PlatynUI.Technology.UiAutomation.dll"
        debug_assembly_path = (
            Path(__file__).parent
            / f"../../../../PlatynUI.Technology.UiAutomation/bin/Debug/net8.0-windows/{assembly_name}"
            # Path(__file__).parent
            # / f"../../../../PlatynUI.Technology.UiAutomation/bin/Debug/net481/{ASSEMBLY_NAME}"
        )
        runtime_assembly_path = Path(__file__).parent.parent / f"runtime/{kind}/{assembly_name}"

        if debug_assembly_path.exists():
            logger.debug(f"Loading PlatynUI from {debug_assembly_path}")  # noqa: G004
            clr.AddReference(str(debug_assembly_path))
        elif runtime_assembly_path.exists():
            logger.debug(f"Loading PlatynUI from {runtime_assembly_path}")  # noqa: G004
            clr.AddReference(str(runtime_assembly_path))
        else:
            logger.error(
                f"Load PlatynUI failed: Could not find the assembly at {debug_assembly_path} or {runtime_assembly_path}"
            )  # noqa: G004
            raise RuntimeError(
                f"Load PlatynUI failed: Could not find the assembly at {debug_assembly_path} or {runtime_assembly_path}"
            )

    @classmethod
    def adapter(cls) -> "Adapter":
        if cls._adapter is None:
            cls._ensure_loaded()

            from PlatynUI.Technology.UiAutomation import Adapter

            cls._adapter = cast("Adapter", Adapter)

        return cls._adapter

    @classmethod
    def finder(cls) -> "Finder":
        if cls._finder is None:
            cls._ensure_loaded()

            from PlatynUI.Technology.UiAutomation import Finder

            cls._finder = cast("Finder", Finder)

        return cls._finder

    @classmethod
    def mouse_device(cls) -> "MouseDevice":
        if cls._mouse_device is None:
            cls._ensure_loaded()

            from PlatynUI.Technology.UiAutomation import MouseDevice

            cls._mouse_device = cast("MouseDevice", MouseDevice)

        return cls._mouse_device

    @classmethod
    def keyboard_device(cls) -> "KeyboardDevice":
        if cls._keyboard_device is None:
            cls._ensure_loaded()

            from PlatynUI.Technology.UiAutomation import KeyboardDevice

            cls._keyboard_device = cast("KeyboardDevice", KeyboardDevice)

        return cls._keyboard_device

    @classmethod
    def display_device(cls) -> "DisplayDevice":
        if cls._display_device is None:
            cls._ensure_loaded()

            from PlatynUI.Technology.UiAutomation import DisplayDevice

            cls._display_device = cast("DisplayDevice", DisplayDevice)

        return cls._display_device

    @classmethod
    def patterns(cls) -> "Patterns":
        if cls._patterns is None:
            cls._ensure_loaded()

            from PlatynUI.Technology.UiAutomation import Patterns

            cls._patterns = cast("Patterns", Patterns)

        return cls._patterns
