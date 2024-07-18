import inspect
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, overload

from .exceptions import AdapterNotSupportsStrategyError, NotAStrategyTypeError
from .strategybase import StrategyBase
from .strategyimpl import StrategyImplFactory
from .technology import Technology

__all__ = ["Adapter", "TStrategyBase"]

TStrategyBase = TypeVar("TStrategyBase", bound=StrategyBase)


class Adapter(StrategyBase, metaclass=ABCMeta):
    """
    the base adapter
    """

    def __init__(self) -> None:
        super().__init__()
        self._strategy_cache: Dict[str, StrategyBase] = {}

    strategy_name = "io.platynui.Adapter"

    @property
    @abstractmethod
    def valid(self) -> bool:
        """
        get true if the adapter is valid at this time
        :return:
        """

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def class_name(self) -> str:
        pass

    @property
    def tag_name(self) -> str:
        return ""

    @property
    @abstractmethod
    def role(self) -> str:
        pass

    @property
    @abstractmethod
    def supported_roles(self) -> Set[str]:
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        pass

    @property
    @abstractmethod
    def supported_types(self) -> Set[str]:
        pass

    @property
    @abstractmethod
    def framework_id(self) -> str:
        pass

    @property
    @abstractmethod
    def runtime_id(self) -> str:
        pass

    @property
    def supported_strategies(self) -> Set[str]:
        if self.valid:
            return {
                m.strategy_name
                for m in inspect.getmro(type(self))
                if hasattr(m, "strategy_name") and m.strategy_name is not None
            }

        return set()

    @overload
    def get_strategy(self, strategy_type: Type[TStrategyBase]) -> TStrategyBase: ...

    @overload
    def get_strategy(self, strategy_type: Type[TStrategyBase], raise_exception: bool) -> Optional[TStrategyBase]: ...

    def get_strategy(self, strategy_type: Type[TStrategyBase], raise_exception: bool = True) -> Optional[TStrategyBase]:
        if hasattr(strategy_type, "strategy_name"):
            strategy_name = getattr(strategy_type, "strategy_name")

            if strategy_name in self._strategy_cache:
                result = self._strategy_cache[strategy_name]
                if isinstance(result, strategy_type):
                    return result

            if strategy_name is not None:
                result1 = self
                if isinstance(result1, strategy_type):
                    self._strategy_cache[strategy_name] = result1
                    return result1

                result2 = StrategyImplFactory.find_strategy_impl_for(self, strategy_type)
                if result2 is not None:
                    self._strategy_cache[strategy_name] = result2
                    return result2

                if raise_exception:
                    raise AdapterNotSupportsStrategyError(
                        "adapter not supports the %s strategy" % strategy_name
                        if strategy_name is not None
                        else repr(strategy_type)
                    )
                return None

        if raise_exception:
            raise NotAStrategyTypeError("type %s is not a strategy type" % repr(strategy_type))

        return None

    def supports_strategy(self, strategy_type: Type[TStrategyBase]) -> bool:
        return self.get_strategy(strategy_type, False) is not None

    @property
    @abstractmethod
    def technology(self) -> Technology: ...

    @property
    @abstractmethod
    def parent(self) -> Optional["Adapter"]: ...

    @property
    @abstractmethod
    def children(self) -> List["Adapter"]: ...

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Adapter):
            return self.runtime_id == other.runtime_id

        raise NotImplementedError
