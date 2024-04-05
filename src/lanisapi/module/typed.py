# Needed for convenient type completion. Makes code maybe a bit complicated or less opaque.

from dataclasses import dataclass
from typing import Any

from .standard import *
from .experimental import *
from .module import NotSupportedModule


@dataclass
class TypingExperimentalModules:
    pass


@dataclass
class TypingModules:
    substitution: SubstitutionModule | NotSupportedModule
    experimental: TypingExperimentalModules
    custom: Any


class TypingShortcuts:
    # More pythonic should be property func, I think, but it doesn't work in my case.
    substitution: SubstitutionModule | NotSupportedModule

    experimental: TypingExperimentalModules
    custom: Any
