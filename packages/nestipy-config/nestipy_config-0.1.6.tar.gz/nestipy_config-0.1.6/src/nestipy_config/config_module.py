from typing import Optional, Awaitable, Callable, Union, Type

from nestipy.common import Module
from nestipy.dynamic_module import DynamicModule

from .config_builder import ConfigurableModuleClass, ConfigOption
from .config_service import ConfigService


@Module(
    providers=[
        ConfigService
    ],
    exports=[
        ConfigService
    ],
)
class ConfigModule(ConfigurableModuleClass):

    @classmethod
    def for_root(cls, option: ConfigOption | None = ConfigOption(), is_global: bool = False):
        module: DynamicModule = cls.for_root_app(option)
        module.is_global = option.is_global or is_global
        return module

    @classmethod
    def for_root_async(
            cls,
            value: Optional[ConfigOption] = None,
            factory: Callable[..., Union[Awaitable[ConfigOption], ConfigOption]] = None,
            existing: Union[Type, str] = None,
            use_class: Type = None,
            inject: list = None,
            imports: list = None,
            is_global: bool = False
    ):
        module: DynamicModule = ConfigurableModuleClass.for_root_app_async(
            value, factory, existing, use_class, inject, imports
        )
        module.is_global = is_global
        return module
