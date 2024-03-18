from abc import ABC, abstractmethod
from ..core.helper.exceptions import NotSupportedException


class NotSupportedModule:
    def __getattribute__(self, item):
        raise NotSupportedException("This module is not supported by your school!")

    def __str__(self):
        raise NotSupportedException("This module is not supported by your school!")


class Module(ABC):
    def __init__(self, request):
        self.request = request


class StandardModule(Module):
    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def link(self):
        raise NotImplementedError

    @abstractmethod
    def get(self):
        raise NotImplementedError
