import logging
from typing import Dict, Any, Optional, List

from gpt_automation.impl.setting.setting_utils import SettingGenerator
from gpt_automation.impl.setting.settings_resolver import SettingsManager
from gpt_automation.impl.plugin_impl.plugin_init import PluginManager
from gpt_automation.impl.setting.paths import PathManager


class InitializeConfig:
    def __init__(self, root_dir: str, profile_names: List[str] = None):
        self.path_manager = PathManager(root_dir)
        self.settings_manager = SettingsManager(self.path_manager)
        self.setting_generator = SettingGenerator(self.path_manager)
        self.logger = logging.getLogger(__name__)
        self.plugin_manager = None
        self.root_dir = root_dir
        self.profile_names = profile_names or []

    def initialize(self, plugin_args: Dict[str, Any] = None, file_args: list = None) -> bool:
        """
        Initialize the configuration and plugins
        Returns True if initialization was successful
        """
        try:
            # Check and initialize base settings if needed
            if not self.setting_generator.is_base_config_initialized():
                self.setting_generator.create_base_config_if_needed()
                self.setting_generator.copy_gitignore_template()

            # Load settings
            settings = self.settings_manager.load_settings()

            # Initialize plugin manager if not provided
            if not self.plugin_manager:
                self.plugin_manager = PluginManager(self.path_manager, settings)

            # Setup and load plugins
            self.plugin_manager.setup_and_activate_plugins(
                plugin_args or {},
                file_args or []
            )

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
