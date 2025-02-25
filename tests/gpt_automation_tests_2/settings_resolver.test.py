import unittest
import os
import shutil
from gpt_automation.impl.setting.paths import PathManager, PathResolver, SettingGenerator
from gpt_automation.impl.setting.settings_resolver import SettingsResolver

class TestSettingsResolver(unittest.TestCase):
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
        
        # Initialize settings resolver
        self.settings_resolver = SettingsResolver(self.path_resolver.base_settings_path)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_base_settings_resolution(self):
        settings = self.settings_resolver.resolve_settings()
        self.assertEqual(settings['extends'], "none")
        self.assertEqual(settings['override'], False)
        self.assertEqual(len(settings['plugins']), 3)
        gpt_ignore = next(p for p in settings['plugins'] if p['plugin_name'] == 'gpt_ignore')
        self.assertTrue(gpt_ignore['args']['enable'])
        self.assertEqual(gpt_ignore['args']['ignore_filenames'], [".gitignore", ".gptignore"])

if __name__ == '__main__':
    unittest.main()
