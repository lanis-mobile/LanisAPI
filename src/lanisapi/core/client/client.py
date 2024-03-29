import dataclasses
from typing import Type, Any
from httpx import Cookies

from ..initialization.types import CookieInitialization
from ..helper.apps import get_apps, is_link_supported
from ...module.module import NotSupportedModule, Module, EmptyCustomModules
from ...module.typed import TypingModules, TypingShortcuts, TypingExperimentalModules
from ...module.standard import standard_modules
from ...module.experimental import experimental_modules


class LanisClient(TypingShortcuts):
    def __init__(self, initialization: CookieInitialization, custom_modules: list[Type[Module]] = None) -> None:
        self.request = initialization.request

        self.apps = get_apps(self.request)

        supported_modules = self.__get_modules(standard_modules)

        supported_experimental = self.__get_modules(experimental_modules)
        typed_supported_experimental = TypingExperimentalModules(**supported_experimental)

        setattr(self, "experimental", typed_supported_experimental)
        supported_modules["experimental"] = typed_supported_experimental

        if custom_modules is not None:
            supported_customs = self.__get_modules(custom_modules)
            customs_dataclass = dataclasses.make_dataclass('CustomModules', supported_customs.keys())
            customs_instance = customs_dataclass(**supported_customs)

            setattr(self, "custom", customs_instance)
            supported_modules["custom"] = customs_instance
        else:
            customs_instance = EmptyCustomModules()
            setattr(self, "custom", customs_instance)
            supported_modules["custom"] = customs_instance

        self.modules = TypingModules(**supported_modules)

    # should be OK because it should be protected from the lib user.
    # noinspection PyProtectedMember, PyCallingNonCallable, PyTypeChecker
    def __get_modules(self, module_list: list[Type[Module]]) -> dict[str, Any]:
        supported_modules = {}
        for module in module_list:
            if module._link is None or is_link_supported(module._link, self.apps):
                supported_modules[module._name] = module(request=self.request)
                setattr(self, module._name, supported_modules[module._name])
            else:
                supported_modules[module._name] = NotSupportedModule()
                setattr(self, module._name, NotSupportedModule())

        return supported_modules

    @property
    def cookies(self) -> Cookies:
        return self.request.cookies

    def is_supported(self, module: Module) -> bool:
        # noinspection PyProtectedMember
        return is_link_supported(module._link, self.apps)
