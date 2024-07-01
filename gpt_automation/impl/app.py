from gpt_automation.impl.config.config_manager import ConfigManager
from gpt_automation.impl.plugin_impl.plugin_manager import PluginManager
from gpt_automation.impl.config.paths import PathManager


class App:
    def __init__(self, root_dir, profile_names):
        self.root_dir = root_dir
        self.profile_names = profile_names
        self.path_manager = PathManager(root_dir)
        self.config_manager = ConfigManager(self.path_manager)
        self.config = self.load_config()
        self.plugin_manager = PluginManager(profile_names, self.config)
        self.load_plugins()

    def load_config(self):
        """ Load and resolve configuration for the specified profiles. """
        try:
            return self.config_manager.get_config(self.profile_names)
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            return None

    def load_plugins(self):
        """ Load and initialize plugins. """
        if not self.config:
            print("Configuration not loaded. Cannot proceed with loading plugins.")
            return False
        try:
            self.plugin_manager.load_plugin_classes()
            self.plugin_manager.create_plugin_instances()
            print("Plugins loaded successfully.")
        except Exception as e:
            print(f"Error initializing plugins: {str(e)}")
            return False
        return True

    def create_profiles(self):
        """ Initialize configurations and load plugins. """
        if not self.config_manager.create_profiles(self.profile_names):
            return False
        self.config = self.load_config()
        if not self.config:
            return False
        self.load_plugins()
        self.plugin_manager.register_plugin_and_create_config()
        return True

    def check_profiles_created(self):
        """ Check if profiles are created. """
        return self.config_manager.check_profiles_created(self.profile_names)
