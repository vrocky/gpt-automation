from dataclasses import dataclass
from typing import Dict, List, Optional

from gpt_automation.impl.setting.settings_resolver import SettingsManager


@dataclass
class PluginInfo:
    package_name: str
    plugin_name: str
    settings_args: Optional[Dict[str, List[str]]] = None

    def key(self):
        return f"{self.package_name}/{self.plugin_name}"

    @staticmethod
    def from_settings(plugin_settings):
        return PluginInfo(
            package_name=plugin_settings["package_name"],
            plugin_name=plugin_settings["plugin_name"],
            settings_args=plugin_settings.get("args"),
            #enable=plugin_config.get("enable", False),
        )


class PluginSettings:
    def __init__(self, settings):
        self.settings = settings


    def get_plugin_settings(self):
        # This method is simplified as we now expect the entire setting to be loaded and handled outside this class
        return self.settings.get('plugins', [])

    def get_all_plugins(self):
        plugins_config = self.get_plugin_settings()
        return [PluginInfo.from_settings(pc) for pc in plugins_config]


