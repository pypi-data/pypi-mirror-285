import functools
import inspect
from abc import ABCMeta
from typing import Any, Callable, Optional, TypeVar, Union, overload

__all__ = ["Decorator"]

TCallable = TypeVar("TCallable", bound=Callable[..., Any])


class Decorator(metaclass=ABCMeta):
    """
    A decorator class that you can be extended that allows you to do normal decorators
    with no arguments, or a decorator with arguments

    May be invoked as a simple, argument-less decorator (i.e. `@decorator`) or
    with arguments customizing its behavior (e.g. `@decorator(*args, **kwargs)`).

    To create your own decorators, just extend this class and override the decorate()
    method, the decorate() method should return a method that can call the passed in func
    at some point

    based off of the task decorator in Fabric
    https://github.com/fabric/fabric/blob/master/fabric/decorators.py#L15

    with modifications inspired by --
    https://wiki.python.org/moin/PythonDecoratorLibrary#Class_method_decorator_using_instance
    https://wiki.python.org/moin/PythonDecoratorLibrary#Creating_decorator_with_optional_arguments

    other links --
    http://pythonconquerstheuniverse.wordpress.com/2012/04/29/python-decorators/
    http://stackoverflow.com/questions/739654/
    http://stackoverflow.com/questions/666216/decorator-classes-in-python
    """

    __wrapped = None
    __wrapped_func = False
    __wrapped_class = False
    __wrapped_instance = False

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        instance = super().__new__(cls)

        if instance.is_wrapped_arg(*args, **kwargs):
            instance.set_wrapped(args[0])
            args = args[1:]
            instance.args = args

        else:
            instance.__wrapped = None
            instance.args = args

        instance.kwargs = kwargs
        # here we do some magic stuff to return the class back in case this is a
        # class decorator, we do this so we don't wrap the class, thus causing
        # things like isinstance() checks to fail, and also not making class
        # variables available
        if instance.__wrapped_class:
            if instance.__wrapped_instance:
                decorate_instance = instance
                class_instance = instance.decorate_class(instance.__wrapped, *instance.args, **instance.kwargs)

                class ChildClass(class_instance):
                    def __init__(self, *args, **kwargs):
                        super(ChildClass, self).__init__(*args, **kwargs)
                        decorate_instance.decorate_instance(self, *decorate_instance.args, **decorate_instance.kwargs)

                instance = ChildClass
                instance.__name__ = class_instance.__name__
                instance.__module__ = class_instance.__module__
                # for some reason you can't update a __doc__ on a class
                # http://bugs.python.org/issue12773

            else:
                instance = instance.decorate_class(instance.__wrapped, *instance.args, **instance.kwargs)

        return instance

    @staticmethod
    def is_wrapped_arg(*args: Any, **kwargs: Any) -> bool:
        if len(args) == 1 and len(kwargs) == 0:
            if inspect.isfunction(args[0]) or isinstance(args[0], type) or isinstance(args[0], FuncDecorator):
                return True

        return False

    def set_wrapped(self, wrapped: Any) -> None:
        self.__wrapped = wrapped
        functools.update_wrapper(self, self.__wrapped)
        self.__wrapped_func = False
        self.__wrapped_class = False

        if inspect.isroutine(wrapped):
            self.__wrapped_func = True

        elif isinstance(wrapped, type):
            self.__wrapped_class = True

    @overload
    def __call__(self, _func: TCallable, *args: Any, **kwargs: Any) -> TCallable: ...

    @overload
    def __call__(self, *args: Any, **kwargs: Any) -> Callable[[TCallable], TCallable]: ...

    def __call__(
        self, _func: Optional[TCallable] = None, *args: Any, **kwargs: Any
    ) -> Union[TCallable, Callable[[TCallable], TCallable]]:
        """call is used when there are (...) on the decorator"""
        invoke = True
        if not self.__wrapped:
            self.set_wrapped(_func)
            args = ()
            invoke = False

        if self.__wrapped_func:
            ret = self.decorate_func(self.__wrapped, *self.args, **self.kwargs)

        elif self.__wrapped_class:
            ret = self.decorate_class(self.__wrapped, *self.args, **self.kwargs)

        else:
            raise ValueError("wrapped is not a class or a function")

        if invoke:
            ret = ret(*args, **kwargs)

        if self.__wrapped_instance:
            self.decorate_instance(ret, *self.args, **self.kwargs)

        return ret

    def decorate_func(self, func: TCallable, *decorator_args: Any, **decorator_kwargs: Any)-> TCallable:
        """
        override this in a child class with your own logic, it must return a
        function that calls self.func

        func -- callback -- the function being decorated
        decorator_args -- tuple -- the arguments passed into the decorator (eg, @dec(1, 2))
        decorator_kwargs -- dict -- the named args passed into the decorator (eg, @dec(foo=1))
        """

        raise RuntimeError("decorator {} does not support function decoration".format(self.__class__.__name__))

    def decorate_class(self, cls, *decorator_args, **decorator_kwargs):
        raise RuntimeError("decorator {} does not support class decoration".format(self.__class__.__name__))

    def decorate_instance(self, instance, *decorator_args, **decorator_kwargs):
        raise RuntimeError("decorator {} does not support instance decoration".format(self.__class__.__name__))
