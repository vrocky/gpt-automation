import unittest
import os
import shutil
from unittest.mock import patch, MagicMock
from gpt_automation.impl.setting.paths import PathManager, PathResolver
from gpt_automation.impl.plugin_impl.plugin_init import PluginManager
from gpt_automation.impl.setting.setting_utils import SettingGenerator
from gpt_automation.impl.setting.settings_resolver import SettingsResolver
from pathlib import Path

class TestPluginManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary test directory
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Initialize path management and settings
        self.path_manager = PathManager(self.test_dir)
        self.path_resolver = PathResolver.from_path_manager(self.path_manager)
        self.setting_generator = SettingGenerator(self.path_resolver)
        
        # Generate base settings
        self.setting_generator.create_base_config_if_needed()
        
        # Load settings using resolver
        self.settings_resolver = SettingsResolver(self.path_resolver.base_settings_path)
        self.settings = self.settings_resolver.resolve_settings()

        # Define registry mock and manifest data
        registry_path = os.path.join(os.path.dirname(__file__), '../../gpt_automation/plugin_registry.json')
        plugin_dir = os.path.dirname(registry_path)
        
        # Setup registry mock
        self.registry_patcher = patch('gpt_automation.impl.plugin_impl.plugin_utils.PluginRegistry')
        mock_registry_class = self.registry_patcher.start()
        mock_registry = MagicMock()
        mock_registry.find_registry_path.return_value = registry_path
        mock_registry.get_plugin_path.return_value = Path(plugin_dir)
        mock_registry_class.return_value = mock_registry

        # Setup plugin utils mock
        self.plugin_utils_patcher = patch('gpt_automation.impl.plugin_impl.plugin_utils.PluginUtils')
        mock_plugin_utils_class = self.plugin_utils_patcher.start()
        mock_plugin_utils = MagicMock()
        
        def get_manifest_for_plugin(plugin_info):
            return {
                'module_name': f'gpt_automation.plugins.{plugin_info.plugin_name}',
                'class_name': 'Plugin',
                'name': plugin_info.plugin_name,
                'description': 'Test Plugin',
                'version': '1.0.0',
                'configFilePatterns': ['*']
            }
        
        class MockPlugin:
            def __init__(self):
                pass

        mock_plugin_utils.get_plugin_manifest.side_effect = get_manifest_for_plugin
        mock_plugin_utils.get_plugin_class.return_value = MockPlugin
        mock_plugin_utils.get_plugin_args.return_value = {}
        mock_plugin_utils_class.return_value = mock_plugin_utils

        # Initialize plugin manager
        self.plugin_manager = PluginManager(self.path_manager, self.settings)

    def test_setup_and_activate_plugins(self):
        # Setup and activate plugins
        self.plugin_manager.setup_and_activate_plugins({
            "root_dir": self.test_dir
        }, [])
        
        # Get all plugins
        plugins = self.plugin_manager.get_all_plugins()
        
        # Verify plugins were loaded
        self.assertEqual(len(plugins), 3)  # Default plugins count
        
        # Verify specific default plugins exist
        expected_plugins = [
            "gpt_automation/gpt_ignore",
            "gpt_automation/gpt_include_only",
            "gpt_automation/bw_filter"
        ]
        for plugin_name in expected_plugins:
            self.assertIn(plugin_name, plugins)
            self.assertIsNotNone(plugins[plugin_name].instance)
            self.assertIsNotNone(plugins[plugin_name].context)

    def test_plugin_context_data(self):
        # Setup plugins
        self.plugin_manager.setup_and_activate_plugins({}, [])
        
        # Get all plugins
        plugins = self.plugin_manager.get_all_plugins()
        
        # Check plugin contexts
        for plugin_info in plugins.values():
            self.assertEqual(plugin_info.context.package_name, "gpt_automation")
            self.assertIsNotNone(plugin_info.context.plugin_name)
            self.assertIsNotNone(plugin_info.context.plugin_settings_path)

    def tearDown(self):
        self.registry_patcher.stop()
        self.plugin_utils_patcher.stop()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

if __name__ == '__main__':
    unittest.main()
