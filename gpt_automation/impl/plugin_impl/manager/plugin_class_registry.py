# gpt_automation/plugin_impl/manager/plugin_class_registry.py
from dataclasses import dataclass

from gpt_automation.impl.plugin_impl.reader.plugin_loader import PluginLoader
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


class PluginClassRegistry:
    def __init__(self):
        self.plugin_info_registry = {}
        self.plugin_classes = {}

    def load_plugin_info(self, plugins_config):
        # Assumes plugins_config is already resolved and passed directly
        for plugin_config in plugins_config:
            # Create PluginInfo instance
            plugin_info = PluginInfo(
                package_name=plugin_config["package_name"],
                plugin_name=plugin_config["plugin_name"],
                enable=plugin_config.get("enable", False),
                settings=plugin_config.get("settings")
            )

            # Store plugin info with key generated from PluginInfo
            self.plugin_info_registry[plugin_info.key()] = plugin_info
            print(f"Saved info for plugin {plugin_info.plugin_name}.")

    def load_plugin_classes(self):
        for plugin_info_key, plugin_info in self.plugin_info_registry.items():
            loader = PluginLoader(plugin_info.package_name)
            plugin_class = loader.get_plugin_class(plugin_info.plugin_name)
            self.plugin_classes[plugin_info_key] = plugin_class
            print(f"Loaded class for plugin {plugin_info.plugin_name}.")

    def get_class(self, plugin_info):
        return self.plugin_classes.get(plugin_info.key())
