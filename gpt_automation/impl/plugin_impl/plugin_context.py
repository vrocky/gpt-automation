class PluginContext:
    def __init__(self, plugin_key, package_name, plugin_name, profile_names, plugin_settings_path, root_dir, prompt_dir):
        self.plugin_key = plugin_key
        self.package_name = package_name
        self.plugin_name = plugin_name
        self.profile_names = profile_names
        self.plugin_settings_path = plugin_settings_path
        self.root_dir = root_dir
        self.prompt_dir = prompt_dir

    def to_dict(self):
        """Convert the PluginContext to a dictionary."""
        return {
            'plugin_key': self.plugin_key,
            'package_name': self.package_name,
            'plugin_name': self.plugin_name,
            'profile_names': self.profile_names,
            'plugin_settings_path': self.plugin_settings_path,
            'root_dir': self.root_dir,
            'prompt_dir': self.prompt_dir
        }


class PluginContextBuilder:
    def __init__(self):
        self.plugin_key = None
        self.package_name = None
        self.plugin_name = None
        self.profile_names = []
        self.plugin_settings_path = None
        self.root_dir = '.'
        self.prompt_dir = '.'

    def set_plugin_key(self, plugin_key):
        self.plugin_key = plugin_key
        return self

    def set_package_name(self, package_name):
        self.package_name = package_name
        return self

    def set_plugin_name(self, plugin_name):
        self.plugin_name = plugin_name
        return self

    def set_profile_names(self, profile_names):
        self.profile_names = profile_names
        return self

    def set_plugin_settings_path(self, plugin_settings_path):
        self.plugin_settings_path = plugin_settings_path
        return self

    def set_root_dir(self, root_dir):
        self.root_dir = root_dir
        return self

    def set_prompt_dir(self, prompt_dir):
        self.prompt_dir = prompt_dir
        return self

    def build(self):
        if not all([self.plugin_key, self.package_name, self.plugin_name, self.plugin_settings_path, self.root_dir, self.prompt_dir]):
            raise ValueError("Missing required context information")
        return PluginContext(
            plugin_key=self.plugin_key,
            package_name=self.package_name,
            plugin_name=self.plugin_name,
            profile_names=self.profile_names,
            plugin_settings_path=self.plugin_settings_path,
            root_dir=self.root_dir,
            prompt_dir=self.prompt_dir
        )
