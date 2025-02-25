from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
from gpt_automation.impl.plugin_impl.plugin_context import PluginContextBuilder
from gpt_automation.impl.plugin_impl.plugin_utils import (
    PluginRegistry, ManifestParser, LoadStatus, LoadResult, PluginUtils
)
from gpt_automation.impl.plugin_impl.plugin_interfaces import IPluginLifecycleCallback
from gpt_automation.impl.plugin_impl.plugin_class_loader import PluginClassLoader
from gpt_automation.impl.setting.setting_models import PluginConfig, Settings, PluginArgs
import logging

@dataclass
class PluginInfo:
    package_name: str
    plugin_name: str
    settings_args: Optional[PluginArgs] = None

    def key(self):
        return f"{self.package_name}/{self.plugin_name}"

    @staticmethod
    def from_settings(plugin_config: PluginConfig) -> 'PluginInfo':
        """Create PluginInfo from PluginConfig"""
        return PluginInfo(
            package_name=plugin_config.package_name,
            plugin_name=plugin_config.plugin_name,
            settings_args=plugin_config.args
        )

class PluginSettings:
    def __init__(self, settings: Union[Settings, Dict]):
        if isinstance(settings, dict):
            self.settings = Settings.from_dict(settings)
        else:
            self.settings = settings
        self.package_name = 'gpt_automation'  # Set default package name

    def get_plugin_settings(self) -> List[PluginConfig]:
        """Get all plugin settings from configuration"""
        return self.settings.plugins

    def get_all_plugins(self) -> List[PluginInfo]:
        """Convert settings to PluginInfo objects"""
        return [PluginInfo.from_settings(pc) for pc in self.get_plugin_settings()]

class PluginConfigLoader:
    def __init__(self, 
                 settings: Settings,
                 path_manager: 'PathManager'):
        self.plugin_settings = PluginSettings(settings)
        self.package_name = self.plugin_settings.package_name
        self.path_manager = path_manager
        self.registry = PluginRegistry(self.package_name)
        self.class_loader = PluginClassLoader()
        self.plugin_utils = PluginUtils(self.registry, self.class_loader)
        self.logger = logging.getLogger(__name__)

    def load_all_contexts(self) -> List['PluginContext']:
        """Load all plugin contexts"""
        contexts = []
        for plugin_info in self.plugin_settings.get_all_plugins():
            context = self._load_plugin_context(plugin_info)
            if context:
                contexts.append(context)
        return contexts

    def _load_plugin_context(self, plugin_info: PluginInfo) -> Optional['PluginContext']:
        """Load complete plugin configuration into context"""
        try:
            # Create base context
            context = self._create_context_for_plugin(plugin_info)
            self.logger.info(f"Created context for plugin {plugin_info.plugin_name}")
            
            # Load manifest
            manifest_data = self.plugin_utils.get_plugin_manifest(plugin_info)
            if not manifest_data:
                self.logger.error(f"Failed to load manifest for {plugin_info.plugin_name}")
                return None

            # Load plugin class
            plugin_class = self.plugin_utils.get_plugin_class(manifest_data)
            if not plugin_class:
                self.logger.error(f"Failed to load plugin class for {plugin_info.plugin_name}")
                return None

            # Update context with configuration
            context.plugin_class = plugin_class
            context.manifest_data = manifest_data
            context.plugin_args = self.plugin_utils.get_plugin_args(plugin_info.plugin_name)
            context.settings_args = plugin_info.settings_args or {}
            context.file_patterns = manifest_data.get('configFilePatterns', [])
            
            return context

        except Exception as e:
            self.logger.error(f"Error loading plugin {plugin_info.plugin_name}: {str(e)}")
            return None

    def _create_context_for_plugin(self, plugin_info: PluginInfo) -> 'PluginContext':
        """Create plugin context with necessary information"""
        path = self.path_manager.get_plugin_settings_path(
            plugin_info.package_name, 
            plugin_info.plugin_name
        )
        return PluginContextBuilder() \
            .set_plugin_key(plugin_info.key()) \
            .set_package_name(plugin_info.package_name) \
            .set_plugin_name(plugin_info.plugin_name) \
            .set_plugin_settings_path(path) \
            .build()

class PluginLoader:
    def __init__(self, 
                 context: 'PluginContext',
                 lifecycle_callback: Optional[IPluginLifecycleCallback] = None):
        self.context = context
        self.lifecycle_callback = lifecycle_callback

    def load_and_activate_plugin(self, arguments: Dict[str, Any], file_args: List[str]) -> Optional[Any]:
        """Load and activate plugin using context"""
        identifier = f"{self.context.package_name}/{self.context.plugin_name}"

        try:
            # Create context with all required fields
            full_context = self.context.to_dict()
            full_context.update({
                'root_dir': arguments.get('root_dir', ''),
                'profile_names': arguments.get('profile_names', [])
            })
            
            # Create instance and initialize
            instance = self.context.plugin_class()
            instance.init(full_context)
            
            # Notify lifecycle callback
            if self.lifecycle_callback:
                self.lifecycle_callback.on_plugin_loaded(identifier, instance)
            return instance

        except Exception as e:
            if self.lifecycle_callback:
                self.lifecycle_callback.on_plugin_error(identifier, str(e))
            return None
