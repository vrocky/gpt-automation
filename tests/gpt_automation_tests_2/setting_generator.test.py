import unittest
import os
import shutil
from gpt_automation.impl.setting.paths import PathManager, PathResolver, SettingGenerator

class TestSettingGenerator(unittest.TestCase):
    def setUp(self):
        # Create a temporary test directory
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Initialize PathManager and PathResolver
        self.path_manager = PathManager(self.test_dir)
        self.path_resolver = PathResolver.from_path_manager(self.path_manager)
        self.setting_generator = SettingGenerator(self.path_resolver)

    def tearDown(self):
        # Clean up test directory after tests
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_base_config_creation(self):
        # Test base configuration creation
        self.assertFalse(self.setting_generator.is_base_config_initialized())
        self.setting_generator.create_base_config_if_needed()
        self.assertTrue(self.setting_generator.is_base_config_initialized())
        self.assertTrue(os.path.exists(self.path_resolver.base_settings_path))

    def test_profile_config_creation(self):
        # Test profile configuration creation
        test_profile = "test_profile"
        self.assertFalse(self.setting_generator.is_profile_config_created(test_profile))
        
        self.setting_generator.create_profile_config(test_profile)
        self.assertTrue(self.setting_generator.is_profile_config_created(test_profile))
        self.assertTrue(os.path.exists(self.path_resolver.get_profile_settings_path(test_profile)))

    def test_multiple_profiles_creation(self):
        # Test creating multiple profiles at once
        test_profiles = ["profile1", "profile2", "profile3"]
        self.setting_generator.create_profiles(test_profiles)
        
        for profile in test_profiles:
            self.assertTrue(self.setting_generator.is_profile_config_created(profile))
            self.assertTrue(os.path.exists(self.path_resolver.get_profile_settings_path(profile)))

    def test_gitignore_template_copy(self):
        # Test gitignore template copying
        self.setting_generator.copy_gitignore_template()
        _, dest_path = self.path_resolver.get_gitignore_paths()
        self.assertTrue(os.path.exists(dest_path))

    def test_repeated_initialization(self):
        # Test that repeated initialization doesn't cause issues
        self.setting_generator.create_base_config_if_needed()
        self.setting_generator.create_base_config_if_needed()
        self.assertTrue(self.setting_generator.is_base_config_initialized())

        test_profile = "test_profile"
        self.setting_generator.create_profile_config(test_profile)
        self.setting_generator.create_profile_config(test_profile)
        self.assertTrue(self.setting_generator.is_profile_config_created(test_profile))

if __name__ == '__main__':
    unittest.main()
