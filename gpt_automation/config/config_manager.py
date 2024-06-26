import os
import json
from shutil import copyfile
from gpt_automation.config.config_loader import load_config_from_json
from gpt_automation.config.config_resolver import ConfigResolver


class ConfigManager:
    def __init__(self, generate_dir='.', base_dir='config', profile_dir='profiles', resources_dir='resources'):
        # Setup directory paths based on the generate_dir provided
        self.base_dir = os.path.join(generate_dir, '.gpt', base_dir)
        self.profile_dir = os.path.join(generate_dir, '.gpt', profile_dir)
        source_dir = os.path.dirname(__file__)
        self.resources_dir = os.path.join(source_dir, '..', 'resources')

        self.config_resolver = ConfigResolver(self)  # Initialize the config resolver with a reference to this manager

        if self.initialize_base_config():
            self.initialize_default_profiles()

    def resolve_final_config(self, profile_name):
        return self.config_resolver.resolve_final_config(profile_name)

    def is_base_config_initialized(self):
        """ Check if the base configuration file has been initialized. """
        base_config_path = os.path.join(self.base_dir, 'base_config.json')
        return os.path.exists(base_config_path)

    def is_profile_config_initialized(self, profile_name):
        """ Check if a specific profile configuration file has been initialized. """
        profile_config_path = os.path.join(self.profile_dir, profile_name, 'config.json')
        return os.path.exists(profile_config_path)

    def initialize_base_config(self):
        """ Initialize default base configuration and return True if successful. """
        if not self.is_base_config_initialized():
            os.makedirs(self.base_dir, exist_ok=True)
            template_path = os.path.join(self.resources_dir, 'default_base_config.json')
            copyfile(template_path, os.path.join(self.base_dir, 'base_config.json'))
            print("Default base configuration initialized.")
            return True
        return False

    def initialize_default_profiles(self):
        """ Initialize default profiles based on predefined settings or conditions. """
        # Example profile initialization
        self.initialize_profile_config('example_profile')

    def initialize_profile_config(self, profile_name):
        """ Initialize a profile configuration if the base config exists. """
        if not self.is_base_config_initialized():
            print("Base configuration not initialized. Cannot initialize profile configurations.")
            return
        if not self.is_profile_config_initialized(profile_name):
            os.makedirs(os.path.dirname(os.path.join(self.profile_dir, profile_name, 'config.json')), exist_ok=True)
            template_path = os.path.join(self.resources_dir, 'default_profile_config.json')
            copyfile(template_path, os.path.join(self.profile_dir, profile_name, 'config.json'))
            print(f"Profile configuration for '{profile_name}' initialized.")

    def get_base_config(self):
        return load_config_from_json(os.path.join(self.base_dir, 'base_config.json'))

    def get_global_config(self):
        return load_config_from_json(os.path.join(self.base_dir, 'global_config.json'))

    def get_profile_config(self, profile_name):
        profile_config_path = os.path.join(self.profile_dir, profile_name, 'config.json')
        return load_config_from_json(profile_config_path)

    def initialize_configurations(self):
        """ Initialize both base and profile configurations if base configuration is successful. """
        if self.initialize_base_config():
            # Base configuration initialized successfully, you can now initialize profile configurations
            # This can be modified to initialize specific profiles or based on some conditions
            self.initialize_profile_config('example_profile')  # Example profile initialization


# Example usage
if __name__ == "__main__":
    # Example to specify a different directory for configuration
    cm = ConfigManager(generate_dir='/path/to/desired/location')
    final_config = cm.resolve_final_config('example_profile')
    print(final_config)
