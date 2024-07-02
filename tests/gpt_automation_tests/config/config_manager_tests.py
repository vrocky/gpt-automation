import os
import json
import unittest
from tempfile import TemporaryDirectory

from gpt_automation.config.config import Config
from gpt_automation.impl.setting.settings_manager import SettingsManager

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)  # Ensure cleanup after tests

    def test_base_config_initialization(self):
        # Initialize ConfigManager with the temporary directory
        cm = SettingsManager(generate_dir=self.temp_dir.name)

        # Check if the base setting was initialized
        self.assertTrue(cm.is_base_config_initialized(), "Base setting should be initialized.")

        # Check the contents of the base setting file
        base_config_path = cm.path_manager.get_base_config_path()
        with open(base_config_path, 'r') as file:
            data = json.load(file)
        self.assertIn('extends', data, "Base setting should have an 'extends' key.")
        self.assertEqual(data['extends'], 'none', "Base setting's 'extends' key should be 'none'.")

    def test_profile_config_initialization_after_base_config(self):
        # Initialize ConfigManager with the temporary directory
        profile_name = 'test_profile'
        cm = SettingsManager(generate_dir=self.temp_dir.name)
        cm.initialize_base_config()  # Initialize base setting explicitly for test clarity

        # Initialize profile setting
        cm.create_profile_config(profile_name)

        # Check if the profile setting was initialized
        self.assertTrue(cm.is_profile_config_created(profile_name), "Profile setting should be initialized.")

        # Check the contents of the profile setting file
        profile_config_path = cm.path_manager.get_profile_config_path(profile_name)
        with open(profile_config_path, 'r') as file:
            data = json.load(file)
        self.assertIn('extends', data, "Profile setting should have an 'extends' key.")
        self.assertEqual(data['extends'], 'base', "Profile setting's 'extends' key should be 'base'.")

    def test_resolve_final_config(self):
        # Initialize ConfigManager with the temporary directory
        profile_name = 'test_profile'
        cm = SettingsManager(generate_dir=self.temp_dir.name)
        cm.initialize_base_config()
        cm.create_profile_config(profile_name)

        # Resolve the final configuration
        final_config = cm.resolve_final_config(profile_name)

        # Check aspects of the resolved configuration
        self.assertTrue(isinstance(final_config, Config), "Resolved setting should be a dict.")
        self.assertIn('plugins', final_config.data, "Resolved setting should contain 'plugins'.")
        self.assertIsInstance(final_config.data['plugins'], list, "Plugins should be a list.")

# Run the tests
if __name__ == '__main__':
    unittest.main()
