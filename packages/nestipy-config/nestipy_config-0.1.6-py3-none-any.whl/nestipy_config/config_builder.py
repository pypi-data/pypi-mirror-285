from dataclasses import dataclass, field
from typing import Callable

from nestipy.dynamic_module import ConfigurableModuleBuilder


@dataclass
class ConfigOption:
    folder: str = './'
    is_global: bool = False
    ignore_env_file: bool = False
    load: list[Callable] = field(default_factory=lambda: [])


ConfigurableModuleClass, CONFIG_OPTION = ConfigurableModuleBuilder[ConfigOption]().set_method(
    'for_root_app').build()
