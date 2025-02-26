import os
import shutil
import unittest
from unittest.mock import patch

from gpt_automation.commands.init_command import InitCommand
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
        
        # Initialize settings using InitCommand
        self._initialize_settings()

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

    def _initialize_settings(self):
        init_command = InitCommand(
            root_dir=self.test_root,
            profile_names=self.test_profiles
        )
        init_result = init_command.execute()
        if not init_result:
            raise RuntimeError("Failed to initialize settings")

    def tearDown(self):
        # Ensure prompt command is cleaned up
        if hasattr(self, 'prompt_command'):
            if hasattr(self.prompt_command, 'file_handler'):
                self.prompt_command.file_handler.close()
            if hasattr(self.prompt_command, 'logger'):
                for handler in self.prompt_command.logger.handlers[:]:
                    handler.close()
                    self.prompt_command.logger.removeHandler(handler)
            self.prompt_command.__del__()
        
        # Clean up test directories with retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if os.path.exists(self.test_root):
                    shutil.rmtree(self.test_root)
                break
            except PermissionError:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(0.2 * (attempt + 1))  # Increasing delay between retries
                else:
                    raise  # Re-raise the last exception if all retries failed

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
        """Test behavior with invalid prompt directories"""
        # Test with non-existent directory
        with self.assertRaises(ValueError) as cm:
            PromptCommand(
                root_dir=self.test_root,
                prompt_dir='/invalid/path',
                profiles=self.test_profiles,
                dir_profiles=self.test_profiles,
                content_profiles=self.test_profiles
            )
        self.assertIn("Prompt directory does not exist", str(cm.exception))

        # Test with prompt directory outside root
        outside_dir = os.path.abspath(os.path.join(self.test_root, '..', 'outside'))
        try:
            os.makedirs(outside_dir, exist_ok=True)
            with self.assertRaises(ValueError) as cm:
                PromptCommand(
                    root_dir=self.test_root,
                    prompt_dir=outside_dir,
                    profiles=self.test_profiles,
                    dir_profiles=self.test_profiles,
                    content_profiles=self.test_profiles
                )
            self.assertIn("Prompt directory must be within root directory", str(cm.exception))
        finally:
            if os.path.exists(outside_dir):
                shutil.rmtree(outside_dir)

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

    def test_missing_settings(self):
        # Remove settings directory
        path_manager = PathManager(self.test_root)
        settings_dir = path_manager.settings_base_dir
        if os.path.exists(settings_dir):
            shutil.rmtree(settings_dir)

        # Test execution with missing settings
        result = self.prompt_command.execute()
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
