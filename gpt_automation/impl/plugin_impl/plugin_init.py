from gpt_automation.impl.logging_utils import get_logger
from typing import Dict, Any, List, Union
from dataclasses import dataclass
from gpt_automation.impl.plugin_impl.plugin_loader import (
    PluginLoader, PluginConfigLoader, PluginSettings, PluginInfo
)
from gpt_automation.impl.plugin_impl.plugin_interfaces import (
    IPluginLifecycleCallback, IPluginConfigCallback, IConfigurationCallback
)
from gpt_automation.impl.plugin_impl.utils.plugin_arg_filter import PluginArgFilter
from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.plugin_impl.plugin_context import PluginContext
from gpt_automation.impl.setting.setting_models import Settings
from gpt_automation.impl.base_plugin import BasePlugin

@dataclass
class PluginInstanceInfo:
    instance: BasePlugin
    context: PluginContext

class PluginLifecycleHandler(IPluginLifecycleCallback):
    def __init__(self, plugin_manager: 'PluginManager', logger, context: PluginContext):
        self.plugin_manager = plugin_manager
        self.logger = logger or get_logger('PluginLifecycleHandler')
        self.context = context

    def on_plugin_loaded(self, identifier: str, instance: Any) -> None:
        self.logger.info(f"Plugin {identifier} loaded successfully")
        self.plugin_manager.add_plugin_instance(identifier, instance, self.context)

    def on_plugin_error(self, identifier: str, error: str) -> None:
        self.logger.error(f"Plugin error for {identifier}: {error}")

class PluginConfigCallback(IPluginConfigCallback):
    def __init__(self, logger):
        self.logger = logger or get_logger('PluginConfigCallback')

    def on_config_error(self, identifier: str, error: str) -> None:
        self.logger.error(f"Configuration error for {identifier}: {error}")

class ConfigurationCallback(IConfigurationCallback):
    def __init__(self, plugin_manager: 'PluginManager', logger):
        self.plugin_manager = plugin_manager
        self.logger = logger or get_logger('ConfigurationCallback')

    def create_plugin_loader(self, context: PluginContext) -> 'PluginLoader':
        """Create configured plugin loader"""
        self.logger.info(f"Creating loader for {context.plugin_name}")
        return PluginLoader(
            context=context,
            lifecycle_callback=PluginLifecycleHandler(
                self.plugin_manager,
                self.logger,
                context
            )
        )

    def on_config_loaded(self, identifier: str, context: PluginContext) -> PluginContext:
        self.logger.info(f"Configuration loaded for {identifier}")
        # Opportunity to modify context before returning
        return context

    def on_config_error(self, identifier: str, error: str) -> None:
        self.logger.error(f"Configuration error for {identifier}: {error}")

class PluginManager:
    def __init__(self, path_manager: PathManager, settings: Union[Dict, Settings], log_file: str = None):
        self.settings = Settings.from_dict(settings) if isinstance(settings, dict) else settings
        self.path_manager = path_manager
        self.plugin_infos: Dict[str, PluginInstanceInfo] = {}
        self.logger = get_logger(__name__, log_file)
        self.log_file = log_file

    def add_plugin_instance(self, identifier: str, instance: Any, context: PluginContext) -> None:
        self.plugin_infos[identifier] = PluginInstanceInfo(instance=instance, context=context)

    def setup_and_activate_plugins(self) -> None:
        """Setup and load plugins without initialization"""
        # Get all plugin contexts
        config_loader = PluginConfigLoader(
            settings=self.settings,
            path_manager=self.path_manager,
            log_file=self.log_file
        )
        
        # Load each plugin
        for context in config_loader.load_all_contexts():
            lifecycle_handler = PluginLifecycleHandler(
                self, 
                self.logger,
                context
            )
            loader = PluginLoader(context=context, lifecycle_callback=lifecycle_handler)
            loader.load_and_activate_plugin()

    def get_all_plugins(self) -> Dict[str, PluginInstanceInfo]:
        """Return all plugin information"""
        return self.plugin_infos
