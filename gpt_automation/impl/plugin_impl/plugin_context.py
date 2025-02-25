from dataclasses import dataclass
from typing import Dict, Any, Optional, Type

@dataclass
class PluginContext:
    plugin_key: str
    package_name: str
    plugin_name: str
    plugin_settings_path: str
    plugin_class: Optional[Type] = None
    manifest_data: Dict[str, Any] = None
    plugin_args: Dict[str, Any] = None
    settings_args: Dict[str, Any] = None
    file_patterns: list = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'plugin_key': self.plugin_key,
            'package_name': self.package_name,
            'plugin_name': self.plugin_name,
            'plugin_settings_path': self.plugin_settings_path
        }

class PluginContextBuilder:
    def __init__(self):
        self._plugin_key = None
        self._package_name = None
        self._plugin_name = None
        self._plugin_settings_path = None

    def set_plugin_key(self, plugin_key: str) -> 'PluginContextBuilder':
        self._plugin_key = plugin_key
        return self

    def set_package_name(self, package_name: str) -> 'PluginContextBuilder':
        self._package_name = package_name
        return self

    def set_plugin_name(self, plugin_name: str) -> 'PluginContextBuilder':
        self._plugin_name = plugin_name
        return self

    def set_plugin_settings_path(self, path: str) -> 'PluginContextBuilder':
        self._plugin_settings_path = path
        return self

    def build(self) -> PluginContext:
        return PluginContext(
            plugin_key=self._plugin_key,
            package_name=self._package_name,
            plugin_name=self._plugin_name,
            plugin_settings_path=self._plugin_settings_path
        )
