import os
import json
from shutil import copyfile
from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.setting.settings_resolver import SettingsManager


class InitConfig:
    def __init__(self, root_dir, profile_names, config_args=None, plugin_file_args=None):
        self.root_dir = root_dir
        self.profile_names = profile_names
        self.config_args = config_args or {}
        self.plugin_file_args = plugin_file_args or []
        self.path_manager = PathManager(root_dir)
        self.settings_manager = SettingsManager(self.path_manager)

    def setup_initial_config(self):
        """
        Setup the initial configuration for the application.
        This involves creating necessary directories, initializing configuration files,
        and setting up plugin configurations. It also checks and creates profiles.
        """
        self.create_directories()
        self.initialize_configuration_files()
        self.create_profiles()
        self.initialize_plugin_configs()

    def create_directories(self):
        """Ensure all required directories are created."""
        self.path_manager.ensure_directories()
        print("All necessary directories have been created.")

    def initialize_configuration_files(self):
        """Initialize base and global configuration files if they do not exist."""
        self.settings_manager.create_base_config_if_needed()

    def create_profiles(self):
        """Check and create profile configurations as necessary."""
        if not self.settings_manager.check_profiles_created(self.profile_names):
            self.settings_manager.create_profiles(self.profile_names)
            print(f"Profiles {', '.join(self.profile_names)} have been initialized.")
        else:
            print("All profiles are already initialized.")

    def initialize_plugin_configs(self):
        """Setup initial configurations for all plugins."""
        # Example: Initialize each plugin's configuration
        for plugin_name in self.plugin_file_args:  # Assuming plugin_file_args contain plugin names
            plugin_config_path = self.path_manager.get_plugin_settings_path(plugin_name, "config.json")
            if not os.path.exists(plugin_config_path):
                default_plugin_config = {"enabled": True, "config": {}}
                with open(plugin_config_path, 'w') as file:
                    json.dump(default_plugin_config, file)
                print(f"Default plugin configuration for {plugin_name} created at {plugin_config_path}.")
            else:
                print(f"Plugin configuration for {plugin_name} already exists.")
