import os


class PathManager:
    def __init__(self, base_directory):
        self.base_directory = os.path.abspath(base_directory)
        self.gpt_dir = os.path.join(self.base_directory, '.gpt')
        self.settings_base_dir = os.path.join(self.gpt_dir, 'settings')
        self.config_dir = os.path.join(self.gpt_dir, 'conf')
        self.plugins_dir = os.path.join(self.gpt_dir, 'config')
        self.logs_dir = os.path.join(self.gpt_dir, 'logs')
        self.resources_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'resources')
        self.ensure_directories()

    def ensure_directories(self):
        """ Ensure that all required directories exist, or create them. """
        directories = [
            self.gpt_dir,
            self.settings_base_dir,
            self.config_dir,  # Added this
            self.plugins_dir,
            self.logs_dir
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def get_base_settings_path(self):
        """ Returns the path to the base configuration file. """
        return os.path.join(self.settings_base_dir, 'base_settings.json')

    def get_plugin_settings_path(self, plugin_module: str, plugin_name: str) -> str:
        """Returns the path to the plugin's directory for storing its files."""
        plugin_dir = os.path.join(self.plugins_dir, plugin_module, plugin_name)
        os.makedirs(plugin_dir, exist_ok=True)
        return plugin_dir

class PathResolver:
    def __init__(self, base_settings_path, resources_dir, gpt_dir):
        self.base_settings_path = base_settings_path
        self.resources_dir = resources_dir
        self.gpt_dir = gpt_dir

    @classmethod
    def from_path_manager(cls, path_manager):
        """Create PathResolver instance from PathManager"""
        return cls(
            base_settings_path=path_manager.get_base_settings_path(),
            resources_dir=path_manager.resources_dir,
            gpt_dir=path_manager.gpt_dir
        )

    def get_default_base_config_path(self):
        """Returns path to default base config template"""
        return os.path.join(self.resources_dir, 'default_base_settings.json')

    def get_gitignore_paths(self):
        """Returns source and destination paths for gitignore"""
        template_path = os.path.join(self.resources_dir, '.gitignore_template')
        dest_path = os.path.join(self.gpt_dir, '.gitignore')
        return template_path, dest_path
