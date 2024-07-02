import os
from shutil import copyfile
from gpt_automation.impl.setting.settings_loader import load_config_from_json
from gpt_automation.impl.setting.settings_resolver import SettingsResolver
from gpt_automation.impl.setting.paths import PathManager


class SettingsManager:
    def __init__(self, path_manager):
        self.path_manager = path_manager
        self.config_resolver = SettingsResolver(self.path_manager)

    def check_profiles_created(self, profile_names):
        """ Ensure all specified profiles are initialized. """
        uninitialized_profiles = [name for name in profile_names if not self.is_profile_config_created(name)]
        if uninitialized_profiles:
            print(f"The following profiles need to be initialized: {', '.join(uninitialized_profiles)}")

            return False
        return True

    def get_settings(self, profile_names):
        """ Resolve and merge configurations for given profiles. """

        merged_config = None
        for profile_name in profile_names:
            profile_json = self.path_manager.get_profile_settings_path(profile_name)
            config = self.config_resolver.resolve_json_config(profile_json)
            if merged_config is None:
                merged_config = config
            else:
                merged_config = merged_config.merge(config)
        return merged_config

    def create_base_config_if_needed(self):
        """ Ensure the base configuration is initialized if not already. """
        base_config_path = self.path_manager.get_base_settings_path()
        if not os.path.exists(base_config_path):
            os.makedirs(os.path.dirname(base_config_path), exist_ok=True)
            template_path = os.path.join(self.path_manager.resources_dir, 'default_base_config.json')
            copyfile(template_path, base_config_path)
            print(f"Initialized base configuration folder with 'base_config.json'.")
            return True
        print("Base configuration already exists.")
        return False

    def create_profiles(self, profile_names):
        """ Initialize multiple profiles, ensuring base configuration is initialized first. """
        self.create_base_config_if_needed()

        for profile_name in profile_names:
            self.create_profile_config(profile_name)

        return True

    def create_profile_config(self, profile_name):
        """ Initialize a single profile configuration if it's not already initialized. """
        profile_config_path = self.path_manager.get_profile_settings_path(profile_name)
        if not os.path.exists(profile_config_path):
            profile_dir = os.path.dirname(profile_config_path)
            os.makedirs(profile_dir, exist_ok=True)
            template_path = os.path.join(self.path_manager.resources_dir, 'default_profile_config.json')
            copyfile(template_path, profile_config_path)
            print(f"Initialized profile '{profile_name}' with 'config.json'.")
        else:
            print(f"Profile configuration for '{profile_name}' already exists.")

    def is_profile_config_created(self, profile_name):
        """ Check if a specific profile configuration file has been initialized. """
        return os.path.exists(self.path_manager.get_profile_settings_path(profile_name))


# Example usage
if __name__ == "__main__":
    pathmanager = PathManager('/path/to/desired/location')
    cm = SettingsManager(pathmanager)
    cm.create_base_config_if_needed()
    final_config = cm.getConfig(['example_profile'])
    if final_config:
        print(final_config)
    else:
        print("Failed to resolve final configuration.")
