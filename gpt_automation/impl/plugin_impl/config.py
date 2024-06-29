from dataclasses import dataclass
from typing import Dict, List, Optional


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
    def __init__(self, config_manager=None):
        self.config_manager = config_manager

    def resolve_and_load_configs(self, profile_names):
        if not self.config_manager:
            raise ValueError("Config manager is required to load configurations.")
        config = self.config_manager.resolve_configs(profile_names)
        return config.data['plugins']

    def get_all_plugins(self, profile_names):
        plugins_config = self.resolve_and_load_configs(profile_names)
        return [PluginInfo.from_config(pc) for pc in plugins_config]

    def get_plugin_settings_path(self, package_name, plugin_name):
        if not self.config_manager:
            raise ValueError("Config manager is required to retrieve settings path.")
        return self.config_manager.path_manager.get_plugin_settings_path(package_name, plugin_name)
