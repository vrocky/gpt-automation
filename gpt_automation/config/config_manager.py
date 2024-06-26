import os
from shutil import copyfile
from gpt_automation.config.config_loader import load_config_from_json
from gpt_automation.config.config_resolver import ConfigResolver
from gpt_automation.config.paths import PathManager


class ConfigManager:

    def __init__(self, generate_dir='.'):
        self.path_manager = PathManager(generate_dir)
        self.config_resolver = ConfigResolver(self)

    def check_profiles_initialized(self, profile_names):
        """ Check if all specified profiles are initialized. """
        uninitialized_profiles = [name for name in profile_names if not self.is_profile_config_initialized(name)]
        if uninitialized_profiles:
            print(f"The following profiles need to be initialized: {', '.join(uninitialized_profiles)}")
            return False
        return True

    def resolve_configs(self, profile_names):
        # Check all profiles are initialized before resolving configurations
        if not self.check_profiles_initialized(profile_names):
            return None  # Or handle differently based on your application needs

        merged_config = None
        for profile_name in profile_names:
            profile_json = self.path_manager.get_profile_config_path(profile_name)
            config = self.config_resolver.resolve_json_config(profile_json)
            if merged_config is None:
                merged_config = config
            else:
                merged_config = merged_config.merge(config)
        return merged_config

    def is_base_config_initialized(self):
        return os.path.exists(self.path_manager.get_base_config_path())

    def initialize_base_config(self):
        if not self.is_base_config_initialized():
            os.makedirs(self.path_manager.base_dir, exist_ok=True)
            base_config_path = self.path_manager.get_base_config_path()
            template_path = os.path.join(self.path_manager.resources_dir, 'default_base_config.json')
            copyfile(template_path, base_config_path)
            print(f"Initialized base configuration folder with 'base_config.json'.")
            return True
        print("Base configuration already exists.")
        return False

    def initialize_profiles(self, profile_names):
        # Initialize multiple profiles
        for profile_name in profile_names:
            self.initialize_profile_config(profile_name)

    def initialize_profile_config(self, profile_name):
        if not self.is_base_config_initialized():
            print("Base configuration not initialized. Cannot initialize profile configurations.")
            return
        if not self.is_profile_config_initialized(profile_name):
            profile_dir = os.path.dirname(self.path_manager.get_profile_config_path(profile_name))
            os.makedirs(profile_dir, exist_ok=True)
            profile_config_path = self.path_manager.get_profile_config_path(profile_name)
            template_path = os.path.join(self.path_manager.resources_dir, 'default_profile_config.json')
            copyfile(template_path, profile_config_path)
            print(f"Initialized profile '{profile_name}' with 'config.json'.")
        else:
            print(f"Profile configuration for '{profile_name}' already exists.")

    def get_base_config(self):
        return load_config_from_json(self.path_manager.get_base_config_path())

    def get_global_config(self):
        return load_config_from_json(self.path_manager.get_global_config_path())

    def initialize_configurations(self, profile_names= None):
        if self.initialize_base_config():
            if profile_names is not None:
                self.initialize_profiles(profile_names)

    def initialize_default_profiles(self):
        self.initialize_profile_config('example_profile')

    def get_profile_config(self, profile_name):
        return load_config_from_json(self.path_manager.get_profile_config_path(profile_name))

    def is_profile_config_initialized(self, profile_name):
        """ Check if a specific profile configuration file has been initialized. """
        return os.path.exists(self.path_manager.get_profile_config_path(profile_name))


# Example usage
if __name__ == "__main__":
    cm = ConfigManager(generate_dir='/path/to/desired/location')
    final_config = cm.resolve_final_config('example_profile')
    print(final_config)
