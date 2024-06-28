import os
import json
import unittest
from tempfile import TemporaryDirectory

from gpt_automation.config.config import Config
from gpt_automation.impl.config.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)  # Ensure cleanup after tests

    def test_base_config_initialization(self):
        # Initialize ConfigManager with the temporary directory
        cm = ConfigManager(generate_dir=self.temp_dir.name)

        # Check if the base config was initialized
        self.assertTrue(cm.is_base_config_initialized(), "Base config should be initialized.")

        # Check the contents of the base config file
        base_config_path = cm.path_manager.get_base_config_path()
        with open(base_config_path, 'r') as file:
            data = json.load(file)
        self.assertIn('extends', data, "Base config should have an 'extends' key.")
        self.assertEqual(data['extends'], 'none', "Base config's 'extends' key should be 'none'.")

    def test_profile_config_initialization_after_base_config(self):
        # Initialize ConfigManager with the temporary directory
        profile_name = 'test_profile'
        cm = ConfigManager(generate_dir=self.temp_dir.name)
        cm.initialize_base_config()  # Initialize base config explicitly for test clarity

        # Initialize profile config
        cm.initialize_profile_config(profile_name)

        # Check if the profile config was initialized
        self.assertTrue(cm.is_profile_config_initialized(profile_name), "Profile config should be initialized.")

        # Check the contents of the profile config file
        profile_config_path = cm.path_manager.get_profile_config_path(profile_name)
        with open(profile_config_path, 'r') as file:
            data = json.load(file)
        self.assertIn('extends', data, "Profile config should have an 'extends' key.")
        self.assertEqual(data['extends'], 'base', "Profile config's 'extends' key should be 'base'.")

    def test_resolve_final_config(self):
        # Initialize ConfigManager with the temporary directory
        profile_name = 'test_profile'
        cm = ConfigManager(generate_dir=self.temp_dir.name)
        cm.initialize_base_config()
        cm.initialize_profile_config(profile_name)

        # Resolve the final configuration
        final_config = cm.resolve_final_config(profile_name)

        # Check aspects of the resolved configuration
        self.assertTrue(isinstance(final_config, Config), "Resolved config should be a dict.")
        self.assertIn('plugins', final_config.data, "Resolved config should contain 'plugins'.")
        self.assertIsInstance(final_config.data['plugins'], list, "Plugins should be a list.")

# Run the tests
if __name__ == '__main__':
    unittest.main()
