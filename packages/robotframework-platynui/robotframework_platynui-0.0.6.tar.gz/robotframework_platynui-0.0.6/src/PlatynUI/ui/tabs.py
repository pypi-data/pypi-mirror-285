import typing

from ..core import LocatorScope, context
from . import Control, Item

__all__ = ["TabList", "TabItem"]


@context
class TabItem(Item):
    pass


@context
class TabList(Control):
    def get_items(self, *args, **kwargs) -> typing.List[TabItem]:
        return self.get_all(TabItem, scope=LocatorScope.Children, *args, **kwargs)

    def iter_items(self, *args, **kwargs) -> typing.Iterator[TabItem]:
        return self.iter_all(TabItem, scope=LocatorScope.Children, *args, **kwargs)

    def get_item(self, *args, **kwargs) -> TabItem:
        return self.get(TabItem, scope=LocatorScope.Children, *args, **kwargs)

    def select(self, *args, **kwargs) -> TabItem:
        result = self.get_item(*args, **kwargs)
        result.select()
        return result
