import dataclasses
from abc import ABC, abstractmethod

import httpx

from ..core.helper.exceptions import NotSupportedException


class NotSupportedModule:
    def __getattribute__(self, item) -> None:
        raise NotSupportedException("This module is not supported by your school!")

    def __str__(self) -> None:
        raise NotSupportedException("This module is not supported by your school!")


@dataclasses.dataclass
class EmptyCustomModules:
    pass


class Module(ABC):
    def __init__(self, request: httpx.Client):
        self._request = request

    @property
    @abstractmethod
    def _name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def _link(self) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def get(self):
        raise NotImplementedError
