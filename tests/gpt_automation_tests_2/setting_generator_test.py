import unittest
import os
import shutil
import json
from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.setting.setting_utils import SettingGenerator

class TestSettingGenerator(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_settings_root')
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        self.path_manager = PathManager(self.test_dir)
        self.setting_generator = SettingGenerator(self.path_manager)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_base_config_creation(self):
        self.assertFalse(self.setting_generator.is_base_config_initialized())
        self.setting_generator.create_base_config_if_needed()
        self.assertTrue(self.setting_generator.is_base_config_initialized())
        
        # Verify base settings file exists and is valid JSON
        base_settings_path = self.path_manager.get_base_settings_path()
        self.assertTrue(os.path.exists(base_settings_path))
        
        # Verify settings content
        with open(base_settings_path, 'r') as f:
            settings = json.load(f)
            self.assertIsInstance(settings, dict)
            self.assertIn('extends', settings)
            self.assertIn('plugins', settings)
            self.assertEqual(settings['extends'], 'none')

    def test_gitignore_creation(self):
        self.setting_generator.copy_gitignore_template()
        gitignore_path = os.path.join(self.path_manager.gpt_dir, '.gitignore')
        self.assertTrue(os.path.exists(gitignore_path))
        
        # Verify gitignore content
        with open(gitignore_path, 'r') as f:
            content = f.read().strip()
            self.assertEqual(content, 'logs')  # Match exact content

    def test_repeated_initialization(self):
        # First initialization
        self.setting_generator.create_base_config_if_needed()
        
        # Modify the base settings
        base_settings_path = self.path_manager.get_base_settings_path()
        test_settings = {
            "version": "1.0",
            "test_key": "test_value"
        }
        with open(base_settings_path, 'w') as f:
            json.dump(test_settings, f)
        
        # Second initialization shouldn't overwrite
        self.setting_generator.create_base_config_if_needed()
        
        # Verify settings weren't overwritten
        with open(base_settings_path, 'r') as f:
            settings = json.load(f)
            self.assertEqual(settings["test_key"], "test_value")

    def test_directory_structure(self):
        # Test that all required directories are created
        self.setting_generator.create_base_config_if_needed()
        
        # Verify all required directories exist
        self.assertTrue(os.path.exists(self.path_manager.settings_base_dir))
        self.assertTrue(os.path.exists(self.path_manager.config_dir))
        self.assertTrue(os.path.exists(self.path_manager.logs_dir))
        self.assertTrue(os.path.exists(self.path_manager.plugins_dir))
        
        # Verify settings directory exists
        settings_parent = os.path.dirname(self.path_manager.get_base_settings_path())
        self.assertTrue(os.path.exists(settings_parent))

if __name__ == '__main__':
    unittest.main()
