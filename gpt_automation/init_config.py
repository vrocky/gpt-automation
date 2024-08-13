import os

from gpt_automation.impl.plugin_impl.plugin_init import PluginSettingsInitializer
from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.setting.settings_manager import SettingsManager


class InitConfig:
    def __init__(self, root_dir, profile_names, plugins_config, config_args=None, plugin_file_args=None):
        self.plugin_initializer = None
        self.root_dir = root_dir
        self.profile_names = profile_names
        self.plugins_config = plugins_config  # Dictionary containing plugin configurations
        self.config_args = config_args or {}
        self.plugin_file_args = plugin_file_args or []
        self.path_manager = PathManager(root_dir)
        self.settings_manager = SettingsManager(self.path_manager)

    def setup_initial_config(self, args, file_args):
        """
        Setup the initial configuration for the application including directories, profiles,
        and plugins based on provided specifications.
        """
        self.settings_manager.create_base_config_if_needed()
        self.settings_manager.create_profiles(self.profile_names)

        self.plugin_initializer = PluginSettingsInitializer(self.profile_names, self.root_dir, self.path_manager, settings=self.load_settings())

        self.initialize_and_configure_plugins(args, file_args)
        print("Initial configuration setup is complete.")

    def load_settings(self):
        """ Load and resolve configuration for the specified profiles. """
        try:
            return self.settings_manager.get_settings(self.profile_names)
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            return None

    def initialize_and_configure_plugins(self,args, file_args):
        """
        Initialize and configure plugins using PluginConfigInitializer.
        """
        self.plugin_initializer.initialize_and_configure_plugins(args,file_args)



    def validate_profiles(self):
        """
        Validate that all profiles are properly initialized and configured.
        """
        if not self.settings_manager.check_profiles_created(self.profile_names):
            print("Some profiles are missing and need to be created.")
            return False
        print("All profiles are correctly initialized.")
        return True


# Example usage
if __name__ == "__main__":
    root_directory = '/path/to/application/root'
    profile_names = ['profile1', 'profile2']
    plugins_config = {
        'plugin1': {'enabled': True, 'config': {'setting1': 'value1'}},
        'plugin2': {'enabled': False, 'config': {'setting2': 'value2'}}
    }
    init_config = InitConfig(root_directory, profile_names, plugins_config)
    init_config.setup_initial_config()
    if init_config.validate_profiles():
        print("Setup successful.")
    else:
        print("Setup failed.")
