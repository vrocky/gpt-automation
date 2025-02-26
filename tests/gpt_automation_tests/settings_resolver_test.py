import unittest
import os
import json
import shutil
from gpt_automation.impl.setting.paths import PathManager, PathResolver
from gpt_automation.impl.setting.settings_resolver import SettingsResolver
from gpt_automation.impl.setting.setting_utils import SettingGenerator
from gpt_automation.impl.setting.setting_models import Settings, PluginConfig, PluginArgs

class TestSettingsResolver(unittest.TestCase):
    def setUp(self):
        # Create a temporary test directory
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Initialize path management
        self.path_manager = PathManager(self.test_dir)
        
        # Create test settings file
        self.settings_path = self.path_manager.get_base_settings_path()
        os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
        
        # Test settings data
        self.test_settings = {
            "extends": "none",
            "override": False,
            "plugins": [
                {
                    "plugin_name": "filter_plugin",
                    "package_name": "gpt_automation",
                    "args": {
                        "enable": True,
                        "black_list": ["*.pyc", "__pycache__"],
                        "white_list": ["*.py", "*.json"]
                    }
                },
                {
                    "plugin_name": "gpt_ignore",
                    "package_name": "gpt_automation",
                    "args": {
                        "enable": True,
                        "ignore_filenames": [".gitignore", ".gptignore"]
                    }
                },
                {
                    "plugin_name": "include_only",
                    "package_name": "gpt_automation",
                    "args": {
                        "enable": True,
                        "include_only_filenames": ["*.py", "*.md"]
                    }
                }
            ]
        }
        
        with open(self.settings_path, 'w') as f:
            json.dump(self.test_settings, f)
        
        # Initialize resolver
        self.resolver = SettingsResolver(self.settings_path)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_settings_file_loading(self):
        """Test that settings file is properly loaded"""
        settings = self.resolver.resolve_settings()
        self.assertIsInstance(settings, Settings)
        self.assertEqual(settings.extends, "none")
        self.assertEqual(settings.override, False)

    def test_plugin_config_parsing(self):
        """Test parsing of plugin configurations"""
        settings = self.resolver.resolve_settings()
        self.assertEqual(len(settings.plugins), 3)
        
        # Test first plugin (filter_plugin)
        filter_plugin = next(p for p in settings.plugins if p.plugin_name == 'filter_plugin')
        self.assertEqual(filter_plugin.package_name, "gpt_automation")
        self.assertTrue(filter_plugin.args.enable)
        
        # Test second plugin (gpt_ignore)
        ignore_plugin = next(p for p in settings.plugins if p.plugin_name == 'gpt_ignore')
        self.assertEqual(len(ignore_plugin.args.ignore_filenames), 2)
        self.assertIn(".gitignore", ignore_plugin.args.ignore_filenames)
        
        # Test third plugin (include_only)
        include_plugin = next(p for p in settings.plugins if p.plugin_name == 'include_only')
        self.assertEqual(len(include_plugin.args.include_only_filenames), 2)
        self.assertIn("*.py", include_plugin.args.include_only_filenames)

    def test_missing_settings_file(self):
        """Test handling of missing settings file"""
        os.remove(self.settings_path)
        with self.assertRaises(FileNotFoundError):
            self.resolver.resolve_settings()

    def test_invalid_json_format(self):
        """Test handling of invalid JSON format"""
        with open(self.settings_path, 'w') as f:
            f.write("invalid json content")
        with self.assertRaises(json.JSONDecodeError):
            self.resolver.resolve_settings()

    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        invalid_settings = {
            "extends": "none"
            # Missing other required fields
        }
        with open(self.settings_path, 'w') as f:
            json.dump(invalid_settings, f)
        
        settings = self.resolver.resolve_settings()
        self.assertEqual(settings.plugins, [])  # Should default to empty list
        self.assertFalse(settings.override)  # Should default to False

if __name__ == '__main__':
    unittest.main()
