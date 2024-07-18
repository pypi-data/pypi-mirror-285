from typing import Optional

from PlatynUI.core.types import Rect
from PlatynUI.ui.core.devices.basedisplaydevice import BaseDisplayDevice

from .loader import DotNetInterface


class UiaDisplayDevice(BaseDisplayDevice):
    @property
    def name(self) -> str:
        return "Windows"

    @property
    def bounding_rectangle(self) -> Rect:
        r = DotNetInterface.display_device().GetBoundingRectangle()
        return Rect(r.X, r.Y, r.Width, r.Height)

    def highlight_rect(self, rect: Rect, time: float) -> None:
        DotNetInterface.display_device().HighlightRect(rect.left, rect.top, rect.width, rect.height, time)

    def get_screenshot(self, rect: Rect, format: str, quality: Optional[int]) -> bytearray:
        raise NotImplementedError
