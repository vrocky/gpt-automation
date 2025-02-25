import logging
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

@dataclass
class PluginInstanceInfo:
    instance: Any
    context: PluginContext

class PluginLifecycleHandler(IPluginLifecycleCallback):
    def __init__(self, instance_manager: 'PluginInstanceManager', logger, context: PluginContext):
        self.instance_manager = instance_manager
        self.logger = logger
        self.context = context

    def on_plugin_loaded(self, identifier: str, instance: Any) -> None:
        self.logger.info(f"Plugin {identifier} loaded successfully")
        self.instance_manager.add_plugin_instance(identifier, instance, self.context)

    def on_plugin_error(self, identifier: str, error: str) -> None:
        self.logger.error(f"Plugin error for {identifier}: {error}")

class PluginConfigCallback(IPluginConfigCallback):
    def __init__(self, logger):
        self.logger = logger

    def on_config_error(self, identifier: str, error: str) -> None:
        self.logger.error(f"Configuration error for {identifier}: {error}")

class ConfigurationCallback(IConfigurationCallback):
    def __init__(self, instance_manager: 'PluginInstanceManager', logger):
        self.instance_manager = instance_manager
        self.logger = logger

    def create_plugin_loader(self, context: PluginContext) -> 'PluginLoader':
        """Create configured plugin loader"""
        self.logger.info(f"Creating loader for {context.plugin_name}")
        return PluginLoader(
            context=context,
            lifecycle_callback=PluginLifecycleHandler(
                self.instance_manager,
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

class PluginInstanceManager:
    def __init__(self):
        self.plugin_infos: Dict[str, PluginInstanceInfo] = {}

    def add_plugin_instance(self, identifier: str, instance: Any, context: PluginContext) -> None:
        self.plugin_infos[identifier] = PluginInstanceInfo(instance=instance, context=context)

    def get_all_plugin_visitors(self, prompt_dir):
        visitors = []
        for plugin_info in self.plugin_infos.values():
            if hasattr(plugin_info.instance, 'get_visitors'):
                visitors.extend(plugin_info.instance.get_visitors(prompt_dir))
        return visitors

    def verify_all_plugins_are_configured(self):
        for plugin_info in self.plugin_infos.values():
            if hasattr(plugin_info.instance, 'is_plugin_configured') and not plugin_info.instance.is_plugin_configured():
                return False
        return True

    def get_instances(self) -> Dict[str, Any]:
        """Return all plugin instances"""
        return {k: v.instance for k, v in self.plugin_infos.items()}

    def get_contexts(self) -> Dict[str, PluginContext]:
        """Return all plugin contexts"""
        return {k: v.context for k, v in self.plugin_infos.items()}

    def get_all_info(self) -> Dict[str, PluginInstanceInfo]:
        """Return all plugin information"""
        return self.plugin_infos

class PluginManager:
    def __init__(self, path_manager: PathManager, settings: Union[Dict, Settings]):
        # Convert dict to Settings only if it's a dict
        self.settings = Settings.from_dict(settings) if isinstance(settings, dict) else settings
        self.path_manager = path_manager
        self.plugin_instance_manager = PluginInstanceManager()
        self.logger = logging.getLogger(__name__)

    def setup_and_activate_plugins(self, plugin_args: Dict[str, Any], file_args: List[str]) -> None:
        """Setup and activate plugins"""
        filtered_plugin_args = PluginArgFilter.preprocess_args(plugin_args)
        
        # Get all plugin contexts
        config_loader = PluginConfigLoader(
            settings=self.settings,
            path_manager=self.path_manager
        )
        
        # Load and activate each plugin
        for context in config_loader.load_all_contexts():
            lifecycle_handler = PluginLifecycleHandler(
                self.plugin_instance_manager, 
                self.logger,
                context
            )
            loader = PluginLoader(context=context, lifecycle_callback=lifecycle_handler)
            
            # Just get the instance first
            instance = loader.load_and_activate_plugin()
            
            if instance:
                # Create context with all required fields
                full_context = context.to_dict()
                full_context.update({
                    'root_dir': filtered_plugin_args.get('root_dir', ''),
                    'profile_names': filtered_plugin_args.get('profile_names', [])
                })
                
                # Initialize the plugin
                try:
                    instance.init(full_context)
                except Exception as e:
                    self.logger.error(f"Failed to initialize plugin {context.plugin_name}: {str(e)}")
                    if lifecycle_handler:
                        lifecycle_handler.on_plugin_error(context.plugin_key, str(e))

    def get_all_plugin_visitors(self, prompt_dir):
        return self.plugin_instance_manager.get_all_plugin_visitors(prompt_dir)

    def is_all_plugin_configured(self):
        return self.plugin_instance_manager.verify_all_plugins_are_configured()

    def get_all_instances(self) -> Dict[str, Any]:
        """Return all loaded plugin instances"""
        return self.plugin_instance_manager.get_instances()

    def get_all_contexts(self) -> Dict[str, PluginContext]:
        """Return all plugin contexts"""
        return self.plugin_instance_manager.get_contexts()

    def get_all_plugin_info(self) -> Dict[str, PluginInstanceInfo]:
        """Return all plugin information"""
        return self.plugin_instance_manager.get_all_info()
