import os
import json
from abc import ABC, abstractmethod
from copy import deepcopy

from shutil import copyfile


def load_config_from_json(file_path):
    """Load configuration from a JSON file."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return SettingMerger(data)


class SettingsInterface(ABC):
    @abstractmethod
    def load(self, path):
        """ Load a configuration from a given path. """
        pass

    @abstractmethod
    def merge(self, config_one, config_two):
        """ Merge two configurations. """
        pass

    @abstractmethod
    def initialize_profiles(self, profile_names):
        """ Initialize given profiles. """
        pass

    @abstractmethod
    def is_profile_config_initialized(self, profile_name):
        """ Check if a specific profile's configuration is initialized. """
        pass


class SettingMerger:
    def __init__(self, data):
        self.data = deepcopy(data)

    def merge(self, other):
        merged_data = self._merge_dicts(self.data, other.data)
        return SettingMerger(merged_data)

    def _merge_dicts(self, base, other):
        result = deepcopy(base)
        for key, value in other.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            elif key in result and isinstance(result[key], list) and isinstance(value, list):
                result[key].extend(value)
            else:
                result[key] = deepcopy(value)
        return result

    def __str__(self):
        return json.dumps(self.data, indent=4)



class SettingGenerator:
    def __init__(self, path_resolver):
        self.path_resolver = path_resolver

    def create_base_config_if_needed(self):
        if not os.path.exists(self.path_resolver.base_settings_path):
            os.makedirs(os.path.dirname(self.path_resolver.base_settings_path), exist_ok=True)
            copyfile(self.path_resolver.get_default_base_config_path(), self.path_resolver.base_settings_path)
            print("Base configuration initialized.")
        else:
            print("Base configuration already exists.")

    def is_base_config_initialized(self):
        return os.path.exists(self.path_resolver.base_settings_path)

    def copy_gitignore_template(self):
        template_path, dest_path = self.path_resolver.get_gitignore_paths()
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        if not os.path.exists(dest_path):
            copyfile(template_path, dest_path)
            print(f".gitignore template copied to {dest_path}.")
        else:
            print(".gitignore already exists in the .gpt directory.")
