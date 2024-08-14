import os
from gpt_automation.impl.setting.settings_loader import load_config_from_json
from gpt_automation.impl.setting.settingmerger import SettingMerger


class SettingsResolver:
    def __init__(self, path_manager):
        self.path_manager = path_manager  # Use PathManager directly for resolving paths

    def resolve_json_config(self, json_path):
        # Resolve the full initial configuration from a JSON path
        initial_config = load_config_from_json(json_path)
        # Start the recursive resolution using the loaded setting, passing the directory of the current file
        resolved_config = self._recursive_resolve(SettingMerger(initial_config.data), os.path.dirname(json_path))
        return resolved_config

    def _recursive_resolve(self, config, base_path='.'):
        """Recursively resolve configuration extensions."""
        visited = set()
        return self._resolve_recursive_helper(config, visited, base_path)

    def _resolve_recursive_helper(self, config, visited, base_path):
        """Helper function to manage recursion and visited tracking."""
        extend_path = config.data.get('extends', 'none')

        if extend_path == 'none':
            return config  # Return current setting if no extension path is specified

        if extend_path in visited:
            raise Exception(f"Circular dependency detected in configuration path: {extend_path}")
        visited.add(extend_path)

        # Resolve the configuration path, using the base path for relative path resolution
        parent_config, parent_base_path = self.resolve_config_path(extend_path, base_path)
        resolved_parent_config = self._resolve_recursive_helper(SettingMerger(parent_config.data), visited, parent_base_path)

        return config.merge(resolved_parent_config)

    def resolve_config_path(self, extend_path, base_path):
        """Resolve the correct configuration based on 'extends' path."""
        if extend_path == 'base':
            base_config_path = self.path_manager.get_base_settings_path()
            base_config = load_config_from_json(base_config_path)
            return SettingMerger(base_config.data), self.path_manager.settings_base_dir
        elif extend_path == 'global':
            global_config_path = self.path_manager.get_global_settings_path()
            global_config = load_config_from_json(global_config_path)
            return SettingMerger(global_config.data), self.path_manager.settings_base_dir
        else:
            # If extend_path is not a special keyword, resolve it relative to the base path
            if not os.path.isabs(extend_path):
                extend_path = os.path.join(base_path, extend_path)
            config = load_config_from_json(extend_path)
            return SettingMerger(config.data), os.path.dirname(extend_path)
