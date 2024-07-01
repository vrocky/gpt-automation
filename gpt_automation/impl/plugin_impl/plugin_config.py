from dataclasses import dataclass
from typing import Dict, List, Optional

from gpt_automation.impl.config.config_manager import ConfigManager


@dataclass
class PluginInfo:
    package_name: str
    plugin_name: str
    enable: bool
    settings: Optional[Dict[str, List[str]]] = None

    def key(self):
        return f"{self.package_name}/{self.plugin_name}"

    @staticmethod
    def from_config(plugin_config):
        return PluginInfo(
            package_name=plugin_config["package_name"],
            plugin_name=plugin_config["plugin_name"],
            enable=plugin_config.get("enable", False),
            settings=plugin_config.get("settings")
        )


class PluginConfig:
    def __init__(self, config,path_manager):
        self.config = config
        self.path_manager = path_manager

    def get_plugin_config(self):
        # This method is simplified as we now expect the entire config to be loaded and handled outside this class
        return self.config.data.get('plugins', [])

    def get_all_plugins(self):
        plugins_config = self.get_plugin_config()
        return [PluginInfo.from_config(pc) for pc in plugins_config]

    def get_plugin_settings_path(self, package_name, plugin_name):
        # This method will need to be implemented based on how paths are managed in your new Config structure
        # The example below assumes there is a straightforward mapping to retrieve paths.
        return self.path_manager.get_plugin_settings_path(package_name, plugin_name)
