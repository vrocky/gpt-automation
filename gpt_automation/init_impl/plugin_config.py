import os

from gpt_automation.impl.plugin_impl.plugin_settings import PluginSettings


class PluginConfigInitializer:
    def __init__(self, path_manager):
        self.path_manager = path_manager

    def initialize_plugin_configs(self):
        """Initialize configurations for all plugins."""
        # Load plugin configurations, create default files, etc.
        # Assume that PluginConfig can fetch all necessary plugins
        plugins_config = PluginSettings(self.path_manager).get_all_plugins()
        for plugin_info in plugins_config:
            self.setup_plugin_config(plugin_info)

    def setup_plugin_config(self, plugin_info):
        """Setup configuration files for a specific plugin."""
        config_path = self.path_manager.get_plugin_settings_path(plugin_info.package_name, plugin_info.plugin_name)
        os.makedirs(config_path, exist_ok=True)
        # Copy default configuration files if necessary
