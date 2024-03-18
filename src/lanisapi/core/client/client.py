import dataclasses

from ..initialization.types import CookieInitialization
from ..helper.apps import get_apps, _is_supported
from ...module.standard import standard_modules
from ...module.experimental import experimental_modules
from ...module.module import NotSupportedModule, StandardModule


class LanisClient:
    def __init__(self, initialization: CookieInitialization, experimental = False):
        self.request = initialization.request

        self.apps = get_apps(self.request)

        supported_modules = self.__get_modules(standard_modules)
        supported_modules["experimental"] = None

        if experimental:
            supported_experimental_modules = self.__get_modules(experimental_modules)
            experimental_modules_class = dataclasses.make_dataclass('ExperimentalModules', supported_experimental_modules.keys())
            supported_modules["experimental"] = experimental_modules_class(**supported_experimental_modules)

        modules_class = dataclasses.make_dataclass('Modules', supported_modules.keys())

        self.modules = modules_class(**supported_modules)

    def __get_modules(self, module_list: list[StandardModule]):
        supported_modules = {}
        for module in module_list:
            if _is_supported(module.link, self.apps):
                supported_modules[module.name] = module(request=self.request)
                setattr(self, module.name, supported_modules[module.name])
            else:
                supported_modules[module.name] = NotSupportedModule()
                setattr(self, module.name, NotSupportedModule())

        return supported_modules

    @property
    def cookies(self):
        return self.request.cookies

    @staticmethod
    def is_supported(app_link: str):
        return _is_supported(app_link, standard_modules)
