import json
from pathlib import Path
import importlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Any, Optional, List

import os

class LoadStatus(Enum):
    SUCCESS = auto()
    MODULE_NOT_FOUND = auto()
    CLASS_NOT_FOUND = auto()
    INVALID_CLASS = auto()
    MANIFEST_ERROR = auto()
    INITIALIZATION_ERROR = auto()

@dataclass
class LoadResult:
    status: LoadStatus
    message: str
    loaded_item: Optional[Any] = None

class PluginRegistry:
    def __init__(self, package_name: str):
        self.package_name = package_name
        self.package_path = None
        self.registry_path = self.find_registry_path()
        self.registry_data = json.loads(Path(self.registry_path).read_text())
        self.plugin_map = self.parse_registry()

    def find_registry_path(self) -> str:
        package = importlib.import_module(self.package_name)
        package_path = Path(package.__file__).resolve().parent
        self.package_path = package_path
        return package_path / 'plugin_registry.json'

    def get_registry_dir(self) -> str:
        """Get the directory containing the registry file"""
        return os.path.dirname(self.find_registry_path())

    def parse_registry(self):
        return {item['name']: item['path'] for item in self.registry_data['plugins']}

    def get_plugin_path(self, plugin_name):
        if (plugin_name in self.plugin_map):
            return self.package_path / self.plugin_map[plugin_name]
        return None

    def plugin_exists(self, plugin_name):
        return plugin_name in self.plugin_map

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
        return self.manifest_data.get('configFilePatterns', [])

class FilePatternFilter:
    def __init__(self, patterns):
        self.patterns = patterns

    def filter_files(self, files):
        """Filter files based on the patterns specified in the plugin's manifest."""
        filtered_files = []
        for file in files:
            if any(Path(file).match(pattern) for pattern in self.patterns):
                filtered_files.append(file)
        return filtered_files


from gpt_automation.impl.logging_utils import get_logger

class PluginUtils:
    def __init__(self, registry: PluginRegistry, class_loader, log_file: str = None):
        self.registry = registry
        self.class_loader = class_loader
        self.logger = get_logger(__name__, log_file)

    def get_plugin_manifest(self, plugin_info) -> Optional[Dict]:
        """Read plugin manifest"""
        try:
            plugin_path = self.get_plugin_path(plugin_info.plugin_name)
            if not plugin_path:
                return None
                
            manifest_path = plugin_path / 'manifest.json'
            if not manifest_path.exists():
                return None
                
            return json.loads(manifest_path.read_text())
        except Exception:
            return None

    def get_plugin_path(self, plugin_name: str) -> Optional[Path]:
        """Get plugin path"""
        plugin_path = self.registry.get_plugin_path(plugin_name)
        if not plugin_path:
            return None
        return Path(plugin_path)

    def get_plugin_class(self, manifest_data: Dict) -> Optional[Any]:
        """Get plugin class"""
        try:
            manifest_parser = ManifestParser(manifest_data)
            module_name = manifest_parser.get_module_name()
            class_name = manifest_parser.get_class_name()
            self.logger.debug(f"Attempting to load plugin class: module={module_name}, class={class_name}, manifest={manifest_data}")
            class_result = self.class_loader.load_class(module_name, class_name)
            if class_result.status == LoadStatus.SUCCESS:
                return class_result.loaded_item
            else:
                self.logger.error(f"Failed to load plugin class: module={module_name}, class={class_name}")
                self.logger.debug(f"Manifest data: {manifest_data}, status={class_result.status}, message={class_result.message}")
                return None
        except Exception as e:
            self.logger.error(f"Exception while loading plugin class: {e}", exc_info=True)
            self.logger.debug(f"Manifest data: {manifest_data}")
            return None

    def get_plugin_args(self, plugin_name: str) -> Dict[str, Any]:
        """Get plugin arguments from config file"""
        try:
            plugin_path = self.get_plugin_path(plugin_name)
            if plugin_path:
                args_path = plugin_path / 'config.json'
                if args_path.exists():
                    return json.loads(args_path.read_text())
        except Exception:
            pass
        return {}

    def merge_plugin_arguments(self, settings_args: Dict[str, Any], plugin_args: Dict[str, Any]) -> Dict[str, Any]:
        """Merge plugin arguments from multiple sources"""
        return {**settings_args, **plugin_args}

    def filter_files_by_pattern(self, files: List[str], patterns: List[str]) -> List[str]:
        """Filter files using pattern filter"""
        return FilePatternFilter(patterns).filter_files(files)
