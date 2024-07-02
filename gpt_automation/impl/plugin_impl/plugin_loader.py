import json
from pathlib import Path
import importlib
import importlib.util


class PluginRegistry:
    def __init__(self, package_name):
        self.package_name = package_name
        self.package_path = None
        self.registry_path = self.find_registry_path()
        self.registry_data = json.loads(Path(self.registry_path).read_text())
        self.plugin_map = self.parse_registry()

    def find_registry_path(self):
        # Use importlib to find the path to plugin_registry.json
        package = importlib.import_module(self.package_name)
        package_path = Path(package.__file__).resolve().parent
        self.package_path = package_path
        return package_path / 'plugin_registry.json'

    def parse_registry(self):
        # Create a map from plugin name to path
        return {item['name']: item['path'] for item in self.registry_data['plugins']}

    def get_plugin_path(self, plugin_name):
        if plugin_name in self.plugin_map:
            return self.package_path / self.plugin_map[plugin_name]
        else:
            return None  # or raise an exception, depending on your error handling strategy


class ManifestParser:
    def __init__(self, manifest_data):
        self.manifest_data = manifest_data

    def get_module_name(self):
        return self.manifest_data.get('module_name')

    def get_class_name(self):
        return self.manifest_data.get('class_name')

    def get_name(self):
        return self.manifest_data.get('name')

    def get_description(self):
        return self.manifest_data.get('description')

    def get_version(self):
        return self.manifest_data.get('version')

    def get_author(self):
        return self.manifest_data.get('author')

    def get_package_name(self):
        return self.manifest_data.get('package_name')

    def get_config_file_patterns(self):
        return self.manifest_data.get('configFilePatterns', [])  # Default to an empty list if not specified



class PluginClassLoader:
    @staticmethod
    def get_class(module_name, class_name):
        module = importlib.import_module(module_name)
        return getattr(module, class_name)


class PluginLoader:
    def __init__(self, package_name):
        self.package_name = package_name
        self.registry = PluginRegistry(self.package_name)

    def get_plugin_path(self, plugin_name):
        # Retrieve the path of the plugin from the registry
        plugin_path = self.registry.get_plugin_path(plugin_name)
        if not plugin_path:
            raise FileNotFoundError(f"Plugin {plugin_name} not found in the registry for package {self.package_name}.")
        return plugin_path

    def get_manifest(self, plugin_name):
        # Get the plugin path and load the manifest file
        plugin_path = self.get_plugin_path(plugin_name)
        manifest_path = Path(plugin_path) / 'manifest.json'
        manifest_data = json.loads(manifest_path.read_text())
        return manifest_data

    def get_plugin_class(self, plugin_name):
        # Get the manifest data using the new get_manifest method
        manifest_data = self.get_manifest(plugin_name)
        manifest_parser = ManifestParser(manifest_data)

        # Get the module name and class name from the manifest
        module_name = manifest_parser.get_module_name()
        class_name = manifest_parser.get_class_name()

        # Use the PluginClassLoader to load the class
        return PluginClassLoader.get_class(module_name, class_name)
