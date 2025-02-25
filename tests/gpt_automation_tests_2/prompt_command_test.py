import os
import shutil
import unittest
import json
from unittest.mock import patch

from gpt_automation.commands.prompt_command import PromptCommand
from gpt_automation.impl.setting.paths import PathManager

class TestPromptCommand(unittest.TestCase):
    def setUp(self):
        # Setup test directories
        self.test_root = os.path.join(os.path.dirname(__file__), 'test_prompt_root')
        self.test_prompt_dir = os.path.join(self.test_root, 'test_prompt_dir')
        self.test_profiles = ['test_profile1', 'test_profile2']
        
        # Clean and create test directories
        for dir_path in [self.test_root, self.test_prompt_dir]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
            os.makedirs(dir_path)

        # Create some test files
        self._create_test_files()
        
        # Initialize base settings
        self._setup_base_settings()

        # Create command instance
        self.prompt_command = PromptCommand(
            root_dir=self.test_root,
            prompt_dir=self.test_prompt_dir,
            profiles=self.test_profiles,
            dir_profiles=self.test_profiles,
            content_profiles=self.test_profiles
        )

    def _create_test_files(self):
        # Create test file structure
        test_files = {
            'test1.py': 'print("Hello")\n',
            'test2.txt': 'Sample content\n',
            'subfolder/test3.md': '# Test markdown\n'
        }
        
        for file_path, content in test_files.items():
            full_path = os.path.join(self.test_prompt_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

    def _setup_base_settings(self):
        path_manager = PathManager(self.test_root)
        base_settings_path = path_manager.get_base_settings_path()
        os.makedirs(os.path.dirname(base_settings_path), exist_ok=True)
        
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
        # Clean up test directories
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)

    def test_directory_structure_generation(self):
        result = self.prompt_command.execute()
        self.assertTrue(result)
        
        # Verify directory structure was processed
        path_manager = PathManager(self.test_root)
        self.assertTrue(os.path.exists(path_manager.logs_dir))
        
        # Check if test files are accessible
        self.assertTrue(os.path.exists(os.path.join(self.test_prompt_dir, 'test1.py')))
        self.assertTrue(os.path.exists(os.path.join(self.test_prompt_dir, 'subfolder/test3.md')))

    def test_content_generation(self):
        result = self.prompt_command.execute()
        self.assertTrue(result)
        
        # Verify that the log file was created
        log_path = os.path.join(PathManager(self.test_root).logs_dir, 'prompt_command.log')
        self.assertTrue(os.path.exists(log_path))

    @patch('pyperclip.copy')
    def test_clipboard_copy(self, mock_copy):
        self.prompt_command.execute()
        mock_copy.assert_called_once()
        copied_content = mock_copy.call_args[0][0]
        self.assertIn('Directory Structure:', copied_content)

    def test_invalid_prompt_directory(self):
        invalid_command = PromptCommand(
            root_dir=self.test_root,
            prompt_dir='/invalid/path',
            profiles=self.test_profiles,
            dir_profiles=self.test_profiles,
            content_profiles=self.test_profiles
        )
        result = invalid_command.execute()
        self.assertFalse(result)

    def test_directory_only_generation(self):
        command = PromptCommand(
            root_dir=self.test_root,
            prompt_dir=self.test_prompt_dir,
            profiles=self.test_profiles,
            dir_profiles=self.test_profiles,
            content_profiles=self.test_profiles,
            generate_dir=True,
            generate_content=False
        )
        result = command.execute()
        self.assertTrue(result)

    def test_content_only_generation(self):
        command = PromptCommand(
            root_dir=self.test_root,
            prompt_dir=self.test_prompt_dir,
            profiles=self.test_profiles,
            dir_profiles=self.test_profiles,
            content_profiles=self.test_profiles,
            generate_dir=False,
            generate_content=True
        )
        result = command.execute()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
