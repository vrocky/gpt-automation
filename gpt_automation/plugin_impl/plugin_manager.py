import importlib

from gpt_automation.config.config import Config
from gpt_automation.config.config_manager import ConfigManager


class PluginManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.plugins = {}

    def register_plugin(self, plugin_name, plugin):
        self.plugins[plugin_name] = plugin

    def get_all_visitors(self):
        visitors = []
        for plugin in self.plugins.values():
            visitors.extend(plugin.get_visitors())
        return visitors

    def load_plugins(self, profile_names):
        # Retrieve plugins configuration from the config manager using profile names
        config = self.resolve_config(profile_names)
        if not config:
            print("Configuration resolution failed; necessary profiles might be missing.")
            return False
        if config:
            plugins_config = config.data.get('plugins', [])
            for plugin_info in plugins_config:
                module_path = plugin_info['module']
                class_name = plugin_info['class']
                settings = plugin_info['settings']
                # Create a unique plugin name from module_path and class_name
                plugin_name = f"{module_path}.{class_name}"
                context = self.create_context(profile_names, plugin_info)
                module = importlib.import_module(module_path)
                plugin_class = getattr(module, class_name)
                plugin_instance = plugin_class(context, settings)
                # Register the plugin with its unique name
                self.register_plugin(plugin_name, plugin_instance)
        return True

    def resolve_config(self, profile_names):

        config: Config = self.config_manager.resolve_configs(profile_names)
        if config is None:
            print("Configuration resolution failed; necessary profiles might be missing.")
            return False
        return config

    def create_context(self, profile_names, plugin_info):

        module_path = plugin_info['module']
        class_name = plugin_info['class']
        settings = plugin_info['settings']
        # Create a unique plugin name from module_path and class_name
        plugin_name = f"{module_path}.{class_name}"

        # Create a context dictionary that includes profile names, plugin name, and resolves paths to plugin settings
        context = {
            'profile_names': profile_names,
            'plugin_name': plugin_name,
            'plugin_settings_path': self.config_manager.path_manager.get_plugin_settings_path(module_path,class_name)
        }
        return context


