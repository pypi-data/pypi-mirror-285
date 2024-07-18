# SPDX-FileCopyrightText: 2024-present Daniel Biehl <dbiehl@live.de>
#
# SPDX-License-Identifier: MIT
from typing import Any

from robot.api.deco import library
from robot.utils import timestr_to_secs
from robotlibcore import DynamicCore, keyword

from PlatynUI.technology.uiautomation import Locator

from .core.contextbase import ContextBase, ContextFactory
from .core.locatorbase import LocatorBase
from .keywords import Application, Buttons, Keyboard, Mouse, Text, TimeSpan, Wait
from .ui import Element, strategies


def convert_context(value) -> ContextBase:  # type: ignore
    if isinstance(value, ContextBase):
        return value

    if isinstance(value, LocatorBase):
        return ContextFactory.create_context(value)

    return ContextFactory.create_context(Locator(path=value))


def convert_timespan(value) -> TimeSpan:  # type: ignore
    return TimeSpan(timestr_to_secs(value))


def convert_locator(value) -> Locator:  # type: ignore
    return Locator(path=value)


@library(
    converters={
        ContextBase: convert_context,
        Element: convert_context,
        strategies.Activatable: convert_context,
        TimeSpan: convert_timespan,
        Locator: convert_locator,
    }
)
class PlatynUI(DynamicCore):
    def __init__(self) -> None:
        super().__init__([Application(), Buttons(), Text(), Keyboard(), Mouse(), Wait()])
