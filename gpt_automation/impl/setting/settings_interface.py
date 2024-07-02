from abc import ABC, abstractmethod


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
