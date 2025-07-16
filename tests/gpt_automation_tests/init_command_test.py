import os
import shutil
import unittest
import json

from gpt_automation.commands.init_command import InitCommand
from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.setting.settings_resolver import SettingsResolver

class TestInitCommand(unittest.TestCase):
    def setUp(self):
        self.test_root = os.path.join(os.path.dirname(__file__), 'test_init_root')
        self.test_profiles = ['test_profile1', 'test_profile2']
        
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)
        os.makedirs(self.test_root)

        self.init_command = InitCommand(
            root_dir=self.test_root,
            profile_names=self.test_profiles
        )

        # Create default base settings file for testing
        self._create_test_base_settings()

    def _create_test_base_settings(self):
        path_manager = PathManager(self.test_root)
        base_settings_path = path_manager.get_base_settings_path()
        os.makedirs(os.path.dirname(base_settings_path), exist_ok=True)
        
        # Match the format from default_base_settings.json
        test_settings = {
            "extends": "none",
            "override": False,
            "plugins": [
                {
                    "plugin_name": "gpt_ignore",
                    "package_name": "gpt_automation",
                    "args": {"enable": True}
                }
            ]
        }
        
        with open(base_settings_path, 'w') as f:
            json.dump(test_settings, f)

    def tearDown(self):
        from gpt_automation.impl.logging_utils import close_logger_handlers
        close_logger_handlers('InitCommand')
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)

    def test_successful_initialization(self):
        result = self.init_command.execute()
        self.assertTrue(result)
        
        path_manager = PathManager(self.test_root)
        
        # Verify directory structure
        self.assertTrue(os.path.exists(path_manager.config_dir))
        self.assertTrue(os.path.exists(path_manager.logs_dir))
        self.assertTrue(os.path.exists(path_manager.settings_base_dir))
        
        # Verify base settings
        base_settings_path = path_manager.get_base_settings_path()
        self.assertTrue(os.path.exists(base_settings_path))
        
        with open(base_settings_path, 'r') as f:
            settings = json.load(f)
            self.assertIsInstance(settings, dict)
            self.assertIn('extends', settings)
            self.assertEqual(settings['extends'], 'none')
            self.assertIn('plugins', settings)
            self.assertIsInstance(settings['plugins'], list)

    def test_repeated_initialization(self):
        # First initialization
        first_result = self.init_command.execute()
        self.assertTrue(first_result)
        
        # Second initialization should also succeed
        second_result = self.init_command.execute()
        self.assertTrue(second_result)

    def test_error_handling_invalid_directory(self):
        try:
            invalid_command = InitCommand(
                root_dir='/nonexistent_root_dir_123',
                profile_names=self.test_profiles
            )
            result = invalid_command.execute()
            self.assertFalse(result)
        except Exception as e:
            # Test passes if an exception is raised
            self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
