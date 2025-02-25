import logging
import os
from typing import Dict, Any

from gpt_automation.impl.setting.setting_utils import SettingGenerator
from gpt_automation.impl.setting.settings_resolver import SettingsResolver
from gpt_automation.impl.plugin_impl.plugin_init import PluginManager
from gpt_automation.impl.setting.paths import PathManager


class InitCommand:
    def __init__(self, root_dir: str, profile_names: list[str]):
        self.root_dir = root_dir
        self.profile_names = profile_names
        self.path_manager = PathManager(root_dir)
        self.setting_generator = SettingGenerator(self.path_manager)
        self.logger = logging.getLogger(__name__)
        self.plugin_manager = None

    def execute(self):
        try:
            if not os.path.exists(self.root_dir):
                self.logger.error(f"Root directory does not exist: {self.root_dir}")
                return False

            # Initialize base configuration
            if not self.setting_generator.is_base_config_initialized():
                self.setting_generator.create_base_config_if_needed()
                self.setting_generator.copy_gitignore_template()

            # Load settings using SettingsResolver with correct path
            settings_resolver = SettingsResolver(self.path_manager.get_base_settings_path())
            settings = settings_resolver.resolve_settings()

            # Update plugin manager initialization
            self.plugin_manager = PluginManager(path_manager=self.path_manager, settings=settings)

            # Setup and activate plugins
            self.plugin_manager.setup_and_activate_plugins({}, [])

            # Configure plugins
            self._configure_plugins()

            return True

        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            return False

    def _configure_plugins(self):
        """Configure all loaded plugins if needed"""
        plugin_infos = self.plugin_manager.get_all_plugins()
        
        for plugin_id, plugin_info in plugin_infos.items():
            plugin = plugin_info.instance
            try:
                if not plugin.is_plugin_configured():
                    self.logger.info(f"Configuring plugin: {plugin_id}")
                    plugin.configure(self.root_dir, self.profile_names)
                else:
                    self.logger.debug(f"Plugin {plugin_id} already configured")
            except Exception as e:
                self.logger.error(f"Error configuring plugin {plugin_id}: {str(e)}")
