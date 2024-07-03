import os

from gpt_automation.impl.conf.config_loader import ConfigLoader
from gpt_automation.impl.setting.settings_manager import SettingsManager
from gpt_automation.impl.plugin_impl.plugin_manager import PluginManager
from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.directory_walker import DirectoryWalker


class App:
    def __init__(self, root_dir, prompt_dir, profile_names, conf_args, plugin_file_args):
        self.root_dir = root_dir
        self.prompt_dir = prompt_dir
        self.profile_names = profile_names
        self.path_manager = PathManager(root_dir)
        self.settings_manager = SettingsManager(self.path_manager)
        self.settings = self.load_settings()
        self.plugin_manager = None
        self.conf_args = conf_args
        self.plugin_file_args = plugin_file_args

        if not self.is_valid_directory_structure():
            raise ValueError("Error: 'prompt_dir' must be a subdirectory of 'root_dir' or the same as 'root_dir'.")

        self.config_loader = ConfigLoader(self.path_manager.get_config_dir())
        self.load_and_merge_configs()

        self.plugin_manager = PluginManager(self.profile_names, self.root_dir,
                                            self.prompt_dir, self.settings, self.path_manager)
        self.load_plugins()

    def is_valid_directory_structure(self):
        """ Validate that prompt_dir is a subdirectory of root_dir or the same. """
        relative_path = os.path.relpath(self.prompt_dir, self.root_dir)
        return relative_path == '.' or not relative_path.startswith('..')

    def load_and_merge_configs(self):
        """ Load .conf files and merge them into conf_args. """
        self.config_loader.load_configs()
        self.conf_args.update(self.config_loader.get_config())  # Merge external config into internal conf_args





    def load_plugins(self):
        """ Load and initialize plugins. """
        if not self.settings:
            print("Configuration not loaded. Cannot proceed with loading plugins.")
            return False
        try:
            self.plugin_manager.create_plugin_instances(args=self.conf_args,
                                                        file_args=self.plugin_file_args)
            print("Plugins loaded successfully.")
        except Exception as e:
            print(f"Error initializing plugins: {str(e)}")
            return False

    def load_settings(self):
        """ Load and resolve configuration for the specified profiles. """
        try:
            return self.settings_manager.get_settings(self.profile_names)
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            return None

    def create_profiles(self):
        """ Initialize configurations and load plugins. """
        if not self.settings_manager.create_profiles(self.profile_names):
            print("Failed to create profiles.")
            return False
        self.plugin_manager.configure_all_plugins()
        return True

    def check_profiles_created(self):
        """ Check if the necessary profiles are created. """
        return self.settings_manager.check_profiles_created(self.profile_names)

    def get_directory_walker(self):
        """ Gets a DirectoryWalker instance if plugins are correctly configured. """
        if self.plugin_manager and self.plugin_manager.is_all_plugin_configured():
            print("Components initialized successfully.")
            return DirectoryWalker(self.prompt_dir, self.plugin_manager)
        else:
            print("Error: Not all plugins could be configured properly.")
            return None

# Example usage of the modified App class
if __name__ == "__main__":
    app = App('/path/to/root', '/path/to/prompt', ['profile1', 'profile2'], {}, {})
    if app.get_directory_walker():
        # Proceed with using the directory walker
        print("Directory walker is ready to use.")
    else:
        print("Directory walker is not available.")
