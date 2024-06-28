import os
from gpt_automation.impl.config.config_loader import load_config_from_json
from gpt_automation.impl.config.config import Config

class ConfigResolver:
    def __init__(self, config_manager):
        self.config_manager = config_manager

    def resolve_json_config(self, json_path):
        # Resolve the full initial configuration from a JSON path
        initial_config = load_config_from_json(json_path)
        # Start the recursive resolution using the loaded config, passing the directory of the current file
        resolved_config = self._recursive_resolve(Config(initial_config.data), os.path.dirname(json_path))
        return resolved_config

    def _recursive_resolve(self, config, base_path='.'):
        """Recursively resolve configuration extensions."""
        visited = set()
        return self._resolve_recursive_helper(config, visited, base_path)

    def _resolve_recursive_helper(self, config, visited, base_path):
        """Helper function to manage recursion and visited tracking."""
        extend_path = config.data.get('extends', 'none')

        if extend_path == 'none':
            return config

        if extend_path in visited:
            raise Exception(f"Circular dependency detected in configuration path: {extend_path}")
        visited.add(extend_path)

        # Resolve the configuration path, using the base path for relative path resolution
        parent_config, parent_base_path = self.resolve_config_path(extend_path, base_path)
        resolved_parent_config = self._resolve_recursive_helper(Config(parent_config.data), visited, parent_base_path)

        return config.merge(resolved_parent_config)

    def resolve_config_path(self, extend_path, base_path='.'):
        """Resolve the correct configuration based on 'extends' path."""
        if extend_path == 'base':
            base_config = self.config_manager.get_base_config()
            return base_config, self.config_manager.path_manager.base_dir
        elif extend_path == 'global':
            global_config = self.config_manager.get_global_config()
            return global_config, self.config_manager.path_manager.base_dir
        else:
            # Resolve the path relative to the base path if it's not a known keyword
            if not os.path.isabs(extend_path):
                extend_path = os.path.join(base_path, extend_path)
            config = load_config_from_json(extend_path)
            return config, os.path.dirname(extend_path)
