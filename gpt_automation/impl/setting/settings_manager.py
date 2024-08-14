import os
import json
from shutil import copyfile

from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.setting.settings_resolver import SettingsResolver, SettingMerger


class SettingsManager:
    def __init__(self, path_manager):
        self.path_manager = path_manager
        self.settings_resolver = SettingsResolver(path_manager)

    def check_profiles_created(self, profile_names):
        """ Check if all specified profiles are already initialized. """
        missing_profiles = [name for name in profile_names if not self.is_profile_config_created(name)]
        if missing_profiles:
            print(f"The following profiles need to be initialized: {', '.join(missing_profiles)}")
            return False
        return True

    def get_settings(self, profile_names):

        if not profile_names:
            base_config_path = self.path_manager.get_base_settings_path()
            if os.path.exists(base_config_path):
                return self.settings_resolver.resolve_json_config(base_config_path).data
            else:
                print("No base configuration found.")
                return {}

        """ Resolve and merge configurations for given profiles using SettingsResolver. """
        merged_config = SettingMerger({})
        for profile_name in profile_names:
            profile_path = self.path_manager.get_profile_settings_path(profile_name)
            if os.path.exists(profile_path):
                profile_config = self.settings_resolver.resolve_json_config(profile_path)
                merged_config = merged_config.merge(profile_config)
        return merged_config.data

    def create_base_config_if_needed(self):
        """ Ensure the base configuration is initialized if not already. """
        base_config_path = self.path_manager.get_base_settings_path()
        if not os.path.exists(base_config_path):
            os.makedirs(os.path.dirname(base_config_path), exist_ok=True)
            default_base_config = os.path.join(self.path_manager.resources_dir, 'default_base_settings.json')
            copyfile(default_base_config, base_config_path)
            print("Base configuration initialized.")
        else:
            print("Base configuration already exists.")

    def create_profiles(self, profile_names):
        """ Initialize multiple profiles if not already initialized. """
        for profile_name in profile_names:
            self.create_profile_config(profile_name)

    def create_profile_config(self, profile_name):
        """ Initialize a single profile configuration if not already initialized. """
        profile_config_path = self.path_manager.get_profile_settings_path(profile_name)
        if not os.path.exists(profile_config_path):
            os.makedirs(os.path.dirname(profile_config_path), exist_ok=True)
            default_profile_config = os.path.join(self.path_manager.resources_dir, 'default_profile_settings.json')
            copyfile(default_profile_config, profile_config_path)
            print(f"Profile '{profile_name}' initialized.")
        else:
            print(f"Configuration for profile '{profile_name}' already exists.")

    def is_profile_config_created(self, profile_name):
        """ Check if a specific profile configuration file has been initialized. """
        return os.path.exists(self.path_manager.get_profile_settings_path(profile_name))

    def is_base_config_initialized(self):
        """ Check if the base configuration file exists. """
        return os.path.exists(self.path_manager.get_base_settings_path())
