from ..core import ContextBase, context
from . import strategies

__all__ = ["Application"]


@context
class Application(ContextBase):
    default_prefix = "app"

    @property
    def application_name(self) -> str:
        return self.adapter.get_strategy(strategies.Application).application_name

    @property
    def id(self) -> str:
        return self.adapter.get_strategy(strategies.Application).process_id

    @property
    def version(self) -> str:
        return self.adapter.get_strategy(strategies.Application).version

    def exit(self) -> None:
        try:
            return self.adapter.get_strategy(strategies.Application).exit()
        finally:
            self.invalidate()
