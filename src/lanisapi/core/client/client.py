import dataclasses

from ..initialization.types import CookieInitialization
from ..helper.apps import get_apps, _is_supported
from ...module.standard import standard_modules
from ...module.module import NotSupportedModule


class LanisClient:
    def __init__(self, initialization: CookieInitialization):
        self.request = initialization.request

        self.apps = get_apps(self.request)

        supported_apps = {}
        for module in standard_modules:
            if _is_supported(module.link, self.apps):
                supported_apps[module.name] = module(request=self.request)
                setattr(self, module.name, supported_apps[module.name])
            else:
                supported_apps[module.name] = NotSupportedModule()
                setattr(self, module.name, NotSupportedModule())

        modules_class = dataclasses.make_dataclass('modules', supported_apps.keys())

        self.modules = modules_class(**supported_apps)

    @property
    def cookies(self):
        return self.request.cookies

    @staticmethod
    def is_supported(app_link: str):
        return _is_supported(app_link, standard_modules)
