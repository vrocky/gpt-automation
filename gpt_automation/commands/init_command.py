import logging
import os
from typing import Dict, Any

from gpt_automation.impl.setting.setting_utils import SettingGenerator
from gpt_automation.impl.setting.settings_resolver import SettingsResolver
from gpt_automation.impl.plugin_impl.plugin_init import PluginManager
from gpt_automation.impl.setting.paths import PathManager


class InitCommand:
    def __init__(self, root_dir: str, profile_names: list[str]):
        self.root_dir = os.path.abspath(root_dir) if root_dir else os.getcwd()
        self.profile_names = profile_names
        self.path_manager = PathManager(self.root_dir)
        self.setting_generator = SettingGenerator(self.path_manager)
        self.logger = logging.getLogger(__name__)
        self.plugin_manager = None

        # Configure logging format
        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

    def execute(self):
        try:
            self.logger.info(f"Initializing GPT Automation in root directory: {self.root_dir}")
            
            # Create .gpt directory to mark as root
            gpt_dir = os.path.join(self.root_dir, '.gpt')
            if not os.path.exists(gpt_dir):
                os.makedirs(gpt_dir, exist_ok=True)
                self.logger.info(f"Created .gpt directory at: {gpt_dir}")
            
            if not os.path.exists(self.root_dir):
                self.logger.error(f"Root directory does not exist: {self.root_dir}")
                return False

            # Create necessary directories with logging
            self.logger.info("Creating required directory structure...")
            directories = {
                "GPT base directory": self.path_manager.gpt_dir,
                "Configuration directory": self.path_manager.config_dir,
                "Logs directory": self.path_manager.logs_dir,
                "Settings directory": self.path_manager.settings_base_dir,
                "Plugins directory": self.path_manager.plugins_dir
            }

            for dir_name, dir_path in directories.items():
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)
                    self.logger.info(f"Created {dir_name} at: {dir_path}")
                else:
                    self.logger.info(f"{dir_name} already exists at: {dir_path}")

            # Initialize base configuration
            if not self.setting_generator.is_base_config_initialized():
                self.logger.info("Initializing base configuration...")
                self.setting_generator.create_base_config_if_needed()
                self.setting_generator.copy_gitignore_template()
            else:
                self.logger.info("Base configuration already initialized")

            # Load settings
            self.logger.info("Loading settings configuration...")
            settings_resolver = SettingsResolver(self.path_manager.get_base_settings_path())
            settings = settings_resolver.resolve_settings()

            # Initialize plugins
            self.logger.info("Setting up plugin manager...")
            self.plugin_manager = PluginManager(path_manager=self.path_manager, settings=settings)

            self.logger.info("Setting up and activating plugins...")
            self.plugin_manager.setup_and_activate_plugins()

            self.logger.info("Configuring plugins...")
            self._configure_plugins()

            self.logger.info("Initialization completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            return False

    def _configure_plugins(self):
        """Configure all loaded plugins if needed"""
        plugin_infos = self.plugin_manager.get_all_plugins()
        
        self.logger.info(f"Found {len(plugin_infos)} plugins to process")
        configured_plugins = []
        already_configured_plugins = []
        failed_plugins = []

        for plugin_id, plugin_info in plugin_infos.items():
            plugin = plugin_info.instance
            try:
                # Get plugin settings path
                plugin_settings_path = self.path_manager.get_plugin_settings_path(
                    plugin_info.context.package_name,
                    plugin_info.context.plugin_name
                )
                
                # Initialize plugin first
                self.logger.info(f"Initializing plugin: {plugin_id}")
                plugin.init(plugin_settings_path, self.root_dir, self.profile_names)
                
                # Check if plugin needs configuration
                if not plugin.is_plugin_configured():
                    self.logger.info(f"Configuring plugin: {plugin_id}")
                    plugin.configure(self.root_dir, self.profile_names)
                    
                    # Verify configuration was successful
                    if not plugin.is_plugin_configured():
                        error_msg = f"Plugin {plugin_id} configuration verification failed"
                        self.logger.error(error_msg)
                        failed_plugins.append(plugin_id)
                        raise RuntimeError(error_msg)
                    
                    self.logger.info(f"Successfully configured and verified plugin: {plugin_id}")
                    configured_plugins.append(plugin_id)
                else:
                    self.logger.debug(f"Plugin {plugin_id} already configured")
                    already_configured_plugins.append(plugin_id)
                    
            except Exception as e:
                self.logger.error(f"Error with plugin {plugin_id}: {str(e)}")
                self.logger.exception(e)
                failed_plugins.append(plugin_id)
                raise e

        # Summary logging
        if configured_plugins:
            self.logger.info(f"Newly configured plugins: {', '.join(configured_plugins)}")
        if already_configured_plugins:
            self.logger.info(f"Previously configured plugins: {', '.join(already_configured_plugins)}")
        if failed_plugins:
            error_msg = f"Failed to configure plugins: {', '.join(failed_plugins)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
