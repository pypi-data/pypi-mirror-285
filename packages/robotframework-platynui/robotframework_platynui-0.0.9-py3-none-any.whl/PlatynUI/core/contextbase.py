import threading
import time
import weakref
from abc import ABCMeta
from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Type, TypeVar, Union, overload

from typing_extensions import Self

from .adapter import Adapter
from .exceptions import CannotEnsureError, NoLocatorDefinedError, PlatynUiFatalError, PlatyUiError
from .locatorbase import LocatorBase
from .locatorscope import LocatorScope
from .predicate import predicate
from .settings import Settings
from .strategies import NativeProperties, Properties
from .weight_calculator import WeightCalculator

__all__ = ["ContextBase", "TContextBase", "context", "UnknownContext", "ContextFactory"]


class ContextBase(metaclass=ABCMeta):
    default_role: Optional[str] = None
    default_prefix: Optional[str] = None

    _locator: Optional[LocatorBase] = None
    __context_parent: Optional["ContextBase"] = None

    def __init__(
        self,
        locator: LocatorBase = None,
        context_parent: Optional["ContextBase"] = None,
        adapter: Optional[Adapter] = None,
    ) -> None:
        self._context_children: weakref.WeakSet["ContextBase"] = weakref.WeakSet()

        if locator is not None:
            self._locator = locator.copy_from(self._locator)
        else:
            self._locator = self._locator.copy() if self._locator is not None else None

        if self._locator is not None:
            self._locator.context = self

        self.__context_parent = context_parent
        if context_parent is not None and isinstance(context_parent, ContextBase):
            context_parent._context_children.add(self)

        self._adapter = adapter

    def __repr__(self) -> str:
        return "%s(locator=%s)" % (self.__class__.__name__, self.locator)

    @property
    def locator(self) -> LocatorBase:
        if self._locator is None:
            raise NoLocatorDefinedError(f"no locator defined for {self:r}")

        return self._locator

    @locator.setter
    def locator(self, v: LocatorBase) -> None:
        self.invalidate()
        self._locator = v

    @property
    def context_parent(self) -> Optional["ContextBase"]:
        return self.__context_parent

    @context_parent.setter
    def context_parent(self, v: Optional["ContextBase"]) -> None:
        if self.context_parent is not None and isinstance(self.context_parent, ContextBase):
            self.context_parent._context_children.remove(self)
        self.__context_parent = v
        self.invalidate()
        if self.context_parent is not None and isinstance(self.context_parent, ContextBase):
            self.context_parent._context_children.add(self)

    @property
    def adapter(self) -> Adapter:
        self.ensure_that(self._adapter_exists)

        result = self._try_get_adapter(True)

        if result is None:
            raise PlatynUiFatalError("adapter is not valid")

        return result

    @adapter.setter
    def adapter(self, v: Adapter) -> None:
        self._adapter = v

    def _try_get_adapter(self, raise_exception: bool = False) -> Optional[Adapter]:
        if self._adapter is not None and not self._adapter.valid:
            self.invalidate()
        if self._adapter is None:
            self._adapter = self._get_adapter(raise_exception)
        return self._adapter

    def invalidate(self) -> None:
        for c in self._context_children:
            c.invalidate()
        self._adapter = None

    def _get_adapter(self, raise_exception: bool) -> Optional[Adapter]:
        self.ensure_that(self._parent_exists)

        if self._locator is not None:
            return self.locator.technology.adapter_factory.get_adapter(
                self.locator, self.context_parent, type(self), raise_exception
            )
        return None

    def full_repr(self) -> str:
        result = repr(self)
        if self.context_parent is not None:
            return self.context_parent.full_repr() + "." + result
        return result

    @predicate("{0} exists")
    def _adapter_exists(self, raise_exception: bool = False) -> bool:
        self.ensure_that(self._parent_exists)

        a = self._try_get_adapter(raise_exception)

        return a is not None and a.valid

    @predicate("parent for {0} exists")
    def _parent_exists(self) -> bool:
        if self.context_parent is None:
            return True

        return self.context_parent._adapter_exists(True)

    __ensure_that_hooks: List[Callable[["ContextBase"], None]] = []

    @classmethod
    def add_ensure_hook(cls, hook: Callable[["ContextBase"], None]) -> None:
        cls.__ensure_that_hooks.append(hook)

    @classmethod
    def __exec_ensure_that_hooks(cls, the_context: "ContextBase") -> None:
        for hook in cls.__ensure_that_hooks:
            hook(the_context)

    class _ContextBaseLocal(threading.local):
        def __init__(self) -> None:
            self.ensure_that_start_time: Optional[float] = None
            self.ensure_that_raise_exception: Optional[bool] = None
            self.in_ensure_that: int = 0
            self.succeeded_predicates: List[Callable[..., Any]] = []
            self.ensure_timeout: Optional[float] = None

    __thread_local = _ContextBaseLocal()

    def ensure_that(
        self,
        *predicates: Optional[Callable[[], bool]],
        timeout: Optional[float] = None,
        raise_exception: Optional[bool] = None,
    ) -> bool:
        return ContextBase._ensure_that(
            self, *predicates, timeout=timeout, raise_exception=raise_exception, failed_func=self.invalidate
        )

    @staticmethod
    def _ensure_that(
        context: "ContextBase",
        *predicates: Optional[Callable[[], bool]],
        timeout: Optional[float] = None,
        raise_exception: Optional[bool] = None,
        failed_func: Optional[Callable[[], None]] = None,
    ) -> bool:
        if timeout is None:
            timeout = Settings.current().ensure_timeout

        ContextBase.__thread_local.in_ensure_that += 1
        try:
            if ContextBase.__thread_local.in_ensure_that == 1:
                ContextBase.__thread_local.succeeded_predicates = []
                ContextBase.__thread_local.ensure_that_raise_exception = raise_exception
                ContextBase.__thread_local.ensure_timeout = timeout
            else:
                raise_exception = ContextBase.__thread_local.ensure_that_raise_exception

            if raise_exception is None:
                raise_exception = True

            result = False
            set_start_time = False
            if ContextBase.__thread_local.ensure_that_start_time is None:
                ContextBase.__thread_local.ensure_that_start_time = time.time()
                set_start_time = True

            last_exception = None
            last_predicate = None

            try:
                while not result:
                    for p in predicates:
                        # skip empty predicates
                        if p is None:
                            continue

                        if not callable(p):
                            raise PlatynUiFatalError("%s is not callable " % p)

                        if p in ContextBase.__thread_local.succeeded_predicates:
                            result = True
                            continue

                        last_predicate = p
                        try:
                            ContextBase.__exec_ensure_that_hooks(context)

                            result = p()

                            if not result:
                                ContextBase.__thread_local.succeeded_predicates.clear()
                                break

                            ContextBase.__thread_local.succeeded_predicates.append(p)

                        except (PlatynUiFatalError, KeyboardInterrupt, SystemExit):
                            raise
                        except BaseException as e:
                            last_exception = e
                            result = False
                            break

                    if result:
                        break

                    thread_ensure_that_start_time = ContextBase.__thread_local.ensure_that_start_time
                    thread_local_ensure_timeout = ContextBase.__thread_local.ensure_timeout

                    if thread_local_ensure_timeout is None or thread_ensure_that_start_time is None:
                        raise PlatyUiError("fatal")

                    if time.time() - thread_ensure_that_start_time > thread_local_ensure_timeout:
                        break

                    if not result:
                        time.sleep(Settings.current().ensure_delay)

                        if failed_func is not None:
                            failed_func()

            finally:
                if set_start_time:
                    ContextBase.__thread_local.ensure_that_start_time = None

            if not result and raise_exception:
                raise CannotEnsureError(
                    "cannot ensure that %s%s"
                    % (
                        (
                            "%s" % last_predicate.message.format(context.full_repr())
                            if last_predicate is not None and hasattr(last_predicate, "message")
                            else "%s for %s" % (last_predicate, context)
                        ),
                        (
                            ",\n   because %s"
                            % (last_exception if str(last_exception).strip() != "" else repr(last_exception))
                            if last_exception is not None
                            else ""
                        ),
                    )
                ) from last_exception

            return result
        finally:
            ContextBase.__thread_local.in_ensure_that -= 1
            assert ContextBase.__thread_local.in_ensure_that >= 0

    @property
    def is_valid(self) -> bool:
        return self._adapter is not None and self._adapter.valid

    def exists(self, timeout: Optional[float] = None, raise_exception: bool = False) -> bool:
        if timeout is None:
            timeout = Settings.current().exists_timeout

        return self.ensure_that(self._adapter_exists, timeout=timeout, raise_exception=raise_exception)

    @property
    def name(self) -> str:
        return self.adapter.name

    @property
    def class_name(self) -> str:
        return self.adapter.class_name

    @property
    def tag_name(self) -> str:
        return self.adapter.tag_name

    @property
    def role(self) -> str:
        return self.adapter.role

    @property
    def supported_roles(self) -> Set[str]:
        return self.adapter.supported_roles

    @property
    def supported_strategies(self) -> Set[str]:
        return self.adapter.supported_strategies

    @property
    def framework_id(self) -> str:
        return self.adapter.framework_id

    @property
    def runtime_id(self) -> Any:
        self.ensure_that(self._adapter_exists, raise_exception=False)

        if not self.is_valid:
            return self

        return self.adapter.runtime_id

    def __enter__(self) -> "Self":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> False:
        pass

    def get(
        self, context_class: Optional[Type["TContextBase"]], *args: Any, locator: LocatorBase = None, **kwargs: Any
    ) -> "TContextBase":
        if locator is None:
            if self.locator is None:
                raise NoLocatorDefinedError("no locator defined for %s" % self)

            locator = self.locator.create_children_locator(*args, **kwargs)

        return locator.copy().create_context(self, context_class)

    def ancestor(
        self, context_class: Optional[Type["TContextBase"]], *args: Any, locator: LocatorBase = None, **kwargs: Any
    ) -> "TContextBase":
        return self.get(context_class, scope=LocatorScope.Ancestor, locator=locator, *args, **kwargs)

    def ancestors(
        self, context_class: Optional[Type["TContextBase"]], *args: Any, locator: LocatorBase = None, **kwargs: Any
    ) -> List["TContextBase"]:
        return self.get_all(context_class, scope=LocatorScope.Ancestor, locator=locator, *args, **kwargs)

    def get_child(
        self, context_class: Optional[Type["TContextBase"]], *args: Any, locator: LocatorBase = None, **kwargs: Any
    ) -> "TContextBase":
        return self.get(context_class, scope=LocatorScope.Children, locator=locator, *args, **kwargs)

    def iter_all(
        self,
        context_class: Optional[Type["TContextBase"]],
        *args: Any,
        locator: Optional[LocatorBase] = None,
        **kwargs: Any,
    ) -> Iterator["TContextBase"]:
        if locator is None:
            if self.locator is None:
                raise NoLocatorDefinedError("no locator defined for %s" % self)

            locator = self.locator.create_children_locator(*args, **kwargs)

        children = self.locator.technology.adapter_factory.get_children_adapters(self, context_class, locator)

        for a in children:
            loc = locator.make_unique_locator(a)
            res = loc.create_context(self, ContextFactory.find_context_class_for(a, context_class))
            res.adapter = a
            if context_class is None or isinstance(res, context_class):
                yield res

    def get_all(
        self, context_class: Optional[Type["TContextBase"]], *args: Any, locator: LocatorBase = None, **kwargs: Any
    ) -> List["TContextBase"]:
        return list(self.iter_all(context_class, *args, locator=locator, **kwargs))

    def get_children(
        self, context_class: Optional[Type["TContextBase"]], *args: Any, locator: LocatorBase = None, **kwargs: Any
    ) -> List["TContextBase"]:
        return self.get_all(context_class, scope=LocatorScope.Children, locator=locator, *args, **kwargs)

    @property
    def parent(self) -> Optional["ContextBase"]:
        adapter = self.adapter

        if adapter is None or not adapter.valid:
            return None

        parent = adapter.parent
        if parent is None:
            return None

        loc = self.locator.create_parent_locator(parent)

        result: "ContextBase" = loc.create_context(self, ContextFactory.find_context_class_for(parent))
        result.adapter = parent

        return result

    def __iter__(self) -> Iterator["ContextBase"]:
        adapter = self.adapter

        if adapter is None or not adapter.valid:
            return

        if self.locator is not None:

            for a in adapter.children:
                loc = self.locator.create_child_locator(a)
                res: ContextBase = loc.create_context(self, ContextFactory.find_context_class_for(a))
                res.adapter = a
                yield res

    @property
    def children(self) -> List["ContextBase"]:
        return list(self)

    def get_properties(self) -> List[str]:
        self.ensure_that(self._adapter_exists)

        return self.adapter.get_strategy(Properties).get_property_names()

    def get_property_value(self, name: str) -> Any:
        self.ensure_that(self._adapter_exists)

        return self.adapter.get_strategy(Properties).get_property_value(name)

    def get_native_properties(self) -> List[str]:
        self.ensure_that(self._adapter_exists)

        return self.adapter.get_strategy(NativeProperties).get_native_property_names()

    def get_native_property_value(self, name: str) -> Any:
        self.ensure_that(self._adapter_exists)

        return self.adapter.get_strategy(NativeProperties).get_native_property_value(name)


class UnknownContext(ContextBase):
    pass


TContextBase = TypeVar("TContextBase", bound=ContextBase)


class ContextFactory:
    class Entry:
        def __init__(self, proxy_type: Type[ContextBase], criterias: Dict[str, object]):
            self.proxy_type = proxy_type
            self.criterias = criterias

    registered_adapters: List[Entry] = []

    @classmethod
    def register_context(cls, adapter_cls: Type[ContextBase], criterias: Dict[str, Any]) -> None:
        cls.registered_adapters.append(ContextFactory.Entry(adapter_cls, criterias.copy()))

    @overload
    @classmethod
    def find_context_class_for(cls, adapter: Adapter, context_type: Optional[Type[TContextBase]]) -> Type[TContextBase]:
        pass

    @overload
    @classmethod
    def find_context_class_for(cls, adapter: Adapter) -> Type[ContextBase]:
        pass

    @classmethod
    def find_context_class_for(
        cls, adapter: Adapter, context_type: Optional[Type[TContextBase]] = None
    ) -> Type[Union[TContextBase, ContextBase]]:

        if context_type is not None:
            return context_type

        weights = []
        calculator = WeightCalculator(adapter)

        for e in cls.registered_adapters:
            weights.append((calculator.calculate(e.criterias), e.proxy_type))

        if len(weights) > 0:
            last = sorted(weights, key=lambda x: x[0])[-1]

            if last[0] > 0:
                return last[1]

        return UnknownContext

    @overload
    @classmethod
    def create_context(
        cls,
        locator: "LocatorBase",
        context_type: Optional[Type[TContextBase]],
        parent: Optional["ContextBase"] = None,
    ) -> TContextBase:
        pass

    @overload
    @classmethod
    def create_context(
        cls,
        locator: "LocatorBase",
        context_type: Optional[Type[TContextBase]] = None,
        parent: Optional["ContextBase"] = None,
    ) -> TContextBase:
        pass

    @classmethod
    def create_context(
        cls,
        locator: "LocatorBase",
        context_type: Optional[Type[TContextBase]] = None,
        parent: Optional["ContextBase"] = None,
        raise_error: bool = True,
    ) -> Optional[TContextBase]:
        adapter = locator.technology.adapter_factory.get_adapter(locator, parent, context_type, raise_error)
        if adapter is None:
            return None

        context_type = cls.find_context_class_for(adapter, context_type)

        return context_type(locator, parent, adapter)


@overload
def context(__cls: Type[TContextBase]) -> Type[TContextBase]: ...


@overload
def context(
    *,
    role: Optional[str] = None,
    framework_id: Optional[str] = None,
    class_name: Optional[str] = None,
    tag_name: Optional[str] = None,
    properties: Optional[Dict[str, str]] = None,
    native_properties: Optional[Dict[str, str]] = None,
    **decorator_kwargs: Any,
) -> Callable[[Type[TContextBase]], Type[TContextBase]]: ...


def context(
    __cls: Optional[Type[TContextBase]] = None,
    *,
    role: Optional[str] = None,
    framework_id: Optional[str] = None,
    class_name: Optional[str] = None,
    tag_name: Optional[str] = None,
    properties: Optional[Dict[str, str]] = None,
    native_properties: Optional[Dict[str, str]] = None,
    prefix: Optional[str] = None,
    **decorator_kwargs: Any,
) -> Union[Type[TContextBase], Callable[[Type[TContextBase]], Type[TContextBase]]]:
    def decorator(cls: Type[TContextBase]) -> Type[TContextBase]:

        setattr(cls, "default_role", role or cls.__name__)

        if prefix is not None:
            setattr(cls, "default_prefix", prefix)

        ContextFactory.register_context(
            cls,
            {
                "role": cls.__name__ if role is None else role,
                "framework_id": framework_id,
                "class_name": class_name,
                "tag_name": tag_name,
                "properties": properties,
                "native_properties": native_properties,
                **decorator_kwargs,
            },
        )

        return cls

    if __cls is None:
        return decorator

    return decorator(__cls)
