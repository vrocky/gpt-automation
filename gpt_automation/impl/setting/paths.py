import os

class PathManager:
    def __init__(self, base_directory):
        self.base_directory = os.path.abspath(base_directory)
        self.gpt_dir = os.path.join(self.base_directory, '.gpt')
        self.settings_base_dir = os.path.join(self.gpt_dir, 'settings')
        self.config_dir = os.path.join(self.gpt_dir, 'conf')
        self.profiles_dir = os.path.join(self.gpt_dir, 'profiles')
        self.plugins_dir = os.path.join(self.gpt_dir, 'config')
        self.logs_dir = os.path.join(self.gpt_dir, 'logs')  # New log directory
        self.resources_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'resources')
        self.ensure_directories()

    def ensure_directories(self):
        """ Ensure that all required directories exist, or create them. """
        os.makedirs(self.gpt_dir, exist_ok=True)
        os.makedirs(self.settings_base_dir, exist_ok=True)
        os.makedirs(self.profiles_dir, exist_ok=True)
        os.makedirs(self.plugins_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)  # Ensure log directory exists

    def get_root_directory(self):
        """ Returns the root (base) directory. """
        return self.base_directory

    def get_gpt_dir(self):
        """ Returns the path to the .gpt directory. """
        return self.gpt_dir

    def get_config_dir(self):
        """ Returns the path to the config directory. """
        return self.config_dir

    def get_logs_dir(self):
        """ Returns the path to the log directory. """
        return self.logs_dir

    def get_base_settings_path(self):
        """ Returns the path to the base configuration file. """
        return os.path.join(self.settings_base_dir, 'base_settings.json')

    def get_global_settings_path(self):
        """ Returns the path to the global configuration file. """
        return os.path.join(self.settings_base_dir, 'global_settings.json')

    def get_profile_settings_path(self, profile_name):
        """ Returns the path to the configuration file for a specific profile. """
        profile_path = os.path.join(self.profiles_dir, profile_name, 'settings.json')
        os.makedirs(os.path.dirname(profile_path), exist_ok=True)
        return profile_path

    def get_plugin_settings_path(self, plugin_module, plugin_class):
        """ Returns the path to the settings file for a specific plugin. """
        plugin_settings_path = os.path.join(self.plugins_dir, plugin_module, plugin_class)
        os.makedirs(os.path.dirname(plugin_settings_path), exist_ok=True)
        return plugin_settings_path
