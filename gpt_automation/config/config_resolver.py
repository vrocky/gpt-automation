import os
from gpt_automation.config.config_loader import load_config_from_json
from gpt_automation.config.config import Config  # Ensure this is the correct path


class ConfigResolver:
    def __init__(self, config_manager):
        self.config_manager = config_manager

    def resolve_final_config(self, profile_name):
        initial_config = self.config_manager.get_profile_config(profile_name)
        resolved_config = self._recursive_resolve(Config(initial_config.data))
        return resolved_config.data

    def _recursive_resolve(self, config, visited=None):
        if visited is None:
            visited = set()

        extend_path = config.data.get('extends', 'none')

        if extend_path == 'none':
            return config

        if extend_path in visited:
            raise Exception(f"Circular dependency detected in configuration path: {extend_path}")
        visited.add(extend_path)

        parent_config = self.resolve_config_path(extend_path)
        resolved_parent_config = self._recursive_resolve(Config(parent_config.data), visited)

        return config.merge(resolved_parent_config)

    def resolve_config_path(self, extend_path):
        """ Resolve the correct configuration based on 'extends' path. """
        if extend_path == 'base':
            return self.config_manager.get_base_config()
        elif extend_path == 'global':
            return self.config_manager.get_global_config()
        else:
            # Assume it's a profile name or JSON file
            return self.config_manager.get_profile_config(extend_path)

