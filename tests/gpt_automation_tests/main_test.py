import os
import shutil
import sys
import unittest
from unittest.mock import patch, MagicMock

from gpt_automation.main import main, setup_cli_parser
from gpt_automation.commands.init_command import InitCommand
from gpt_automation.commands.prompt_command import PromptCommand
from gpt_automation.impl.setting.paths import PathManager

class TestMain(unittest.TestCase):
    def setUp(self):
        # Setup test directories
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_main')
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        # Initialize .gpt directory and settings for tests
        os.makedirs(os.path.join(self.test_dir, '.gpt', 'settings'), exist_ok=True)
        with open(os.path.join(self.test_dir, '.gpt', 'settings', 'base_settings.json'), 'w') as f:
            f.write('{"version": "1.0", "plugins": {}}')

        # Create a test prompt directory
        self.test_prompt_dir = os.path.join(self.test_dir, 'prompt_dir')
        os.makedirs(self.test_prompt_dir, exist_ok=True)

        # Add sample project structure
        self.test_project_dir = os.path.join(self.test_dir, 'sample_project')
        os.makedirs(self.test_project_dir)
        self._create_sample_project()

    def _create_sample_project(self):
        """Create a sample project structure for testing"""
        sample_files = {
            'src/main.py': 'def main():\n    print("Hello")',
            'src/utils.py': 'def helper():\n    return "helper"',
            'tests/test_main.py': 'def test_main():\n    assert True',
            'README.md': '# Test Project'
        }
        
        for file_path, content in sample_files.items():
            full_path = os.path.join(self.test_project_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

    def tearDown(self):
        from gpt_automation.impl.logging_utils import close_logger_handlers
        close_logger_handlers('PromptCommand')
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_parser_setup(self):
        parser = setup_cli_parser()
        # Test init command parser
        args = parser.parse_args(['init', '--root_dir', '/test/path'])
        self.assertEqual(args.command, 'init')
        self.assertEqual(args.root_dir, '/test/path')
        self.assertEqual(args.profiles, [])

        # Test prompt command parser
        args = parser.parse_args(['prompt', '--root_dir', '/test/path', 'profile1'])
        self.assertEqual(args.command, 'prompt')
        self.assertEqual(args.root_dir, '/test/path')
        self.assertEqual(args.profiles, ['profile1'])
        self.assertIsNone(args.dir)
        self.assertIsNone(args.content)

    def test_init_command_execution(self):
        """Test init command with root_dir argument"""
        with patch('sys.argv', ['gpt-automation', 'init', '--root_dir', self.test_dir]):
            with patch.object(InitCommand, 'execute') as mock_execute:
                mock_execute.return_value = True
                main()
                mock_execute.assert_called_once()

    def test_prompt_command_execution(self):
        """Test prompt command with root_dir argument"""
        test_args = [
            'gpt-automation',
            'prompt',
            '--root_dir', self.test_dir,
            'test_profile'
        ]
        with patch('sys.argv', test_args):
            with patch.object(PromptCommand, 'execute') as mock_execute:
                mock_execute.return_value = True
                main()
                mock_execute.assert_called_once()

    def test_prompt_command_with_dir_content(self):
        """Test prompt command with all arguments"""
        test_args = [
            'gpt-automation',
            'prompt',
            '--root_dir', self.test_dir,
            '--dir', 'profile1',
            '--content', 'profile2'
        ]
        with patch('sys.argv', test_args):
            with patch.object(PromptCommand, 'execute') as mock_execute:
                mock_execute.return_value = True
                main()
                mock_execute.assert_called_once()

    def test_complete_workflow(self):
        """Test a complete workflow with init and prompt commands"""
        # Step 1: Initialize project
        with patch('sys.argv', ['gpt-automation', 'init', '--root_dir', self.test_dir]):
            with patch.object(InitCommand, 'execute') as mock_init:
                mock_init.return_value = True
                main()
                mock_init.assert_called_once()

        # Step 2: Generate prompts
        with patch('sys.argv', [
            'gpt-automation',
            'prompt',
            '--root_dir', self.test_dir,
            '--prompt_dir', self.test_project_dir
        ]):
            with patch.object(PromptCommand, 'execute') as mock_prompt:
                mock_prompt.return_value = True
                main()
                mock_prompt.assert_called_once()

    def test_profile_based_workflow(self):
        """Test workflow with specific profiles"""
        # Init with profiles
        with patch('sys.argv', [
            'gpt-automation',
            'init',
            '--root_dir', self.test_dir,
            'profile1',
            'profile2'
        ]):
            with patch.object(InitCommand, 'execute') as mock_init:
                mock_init.return_value = True
                main()
                mock_init.assert_called_once()

        # Prompt with specific dir/content profiles
        with patch('sys.argv', [
            'gpt-automation',
            'prompt',
            '--root_dir', self.test_dir,
            '--prompt_dir', self.test_project_dir,
            '--dir', 'profile1',
            '--content', 'profile2'
        ]):
            with patch.object(PromptCommand, 'execute') as mock_prompt:
                mock_prompt.return_value = True
                main()
                mock_prompt.assert_called_once()

    def test_error_workflow(self):
        """Test error handling in workflow"""
        # Test prompt before init
        with patch('sys.argv', [
            'gpt-automation',
            'prompt',
            '--root_dir', self.test_dir,
            '--prompt_dir', self.test_project_dir
        ]):
            with patch.object(PromptCommand, 'execute') as mock_execute:
                mock_execute.return_value = False
                main()
                mock_execute.assert_called_once()

        # Test with non-existent directories
        with patch('sys.argv', [
            'gpt-automation',
            'prompt',
            '--root_dir', '/nonexistent',
            '--prompt_dir', '/also/nonexistent'
        ]):
            with self.assertRaises(ValueError):
                main()

    def test_invalid_command(self):
        with patch('sys.argv', ['gpt-automation', 'invalid_command']):
            with self.assertRaises(SystemExit):
                main()

    def test_prompt_dir_argument(self):
        """Test prompt command with both root_dir and prompt_dir"""
        test_args = [
            'gpt-automation',
            'prompt',
            '--root_dir', self.test_dir,
            '--prompt_dir', self.test_prompt_dir
        ]
        with patch('sys.argv', test_args):
            with patch.object(PromptCommand, 'execute') as mock_execute:
                mock_execute.return_value = True
                main()
                mock_execute.assert_called_once()

if __name__ == '__main__':
    unittest.main()
