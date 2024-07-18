from abc import ABCMeta, abstractmethod

from ..core import adapterfactory

__all__ = ["Technology"]


class Technology(metaclass=ABCMeta):
    """
    the base class for Technologies
    """

    @property
    def name(self) -> str:
        """
        the name of the technology
        """
        return self.__class__.__qualname__

    @property
    @abstractmethod
    def adapter_factory(self) -> adapterfactory.AdapterFactory:
        """
        get's the adapter factory defined by this technology
        """
