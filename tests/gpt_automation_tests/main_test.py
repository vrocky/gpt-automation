import os
import shutil
import sys
import unittest
from unittest.mock import patch, MagicMock

from gpt_automation.main import main, setup_cli_parser
from gpt_automation.commands.init_command import InitCommand
from gpt_automation.commands.prompt_command import PromptCommand

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

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_parser_setup(self):
        parser = setup_cli_parser()
        args = parser.parse_args(['init'])
        self.assertEqual(args.command, 'init')
        self.assertEqual(args.profiles, [])

        args = parser.parse_args(['prompt', 'profile1'])
        self.assertEqual(args.command, 'prompt')
        self.assertEqual(args.profiles, ['profile1'])
        self.assertIsNone(args.dir)
        self.assertIsNone(args.content)

    def test_init_command_execution(self):
        with patch('sys.argv', ['gpt-automation', 'init']):
            with patch.object(InitCommand, 'execute') as mock_execute:
                mock_execute.return_value = True
                main()
                mock_execute.assert_called_once()

    def test_prompt_command_execution(self):
        with patch('sys.argv', ['gpt-automation', 'prompt', 'test_profile', '--root_dir', self.test_dir]):
            with patch.object(PromptCommand, 'execute') as mock_execute:
                mock_execute.return_value = True
                main()
                mock_execute.assert_called_once()

    def test_prompt_command_with_dir_content(self):
        test_args = [
            'gpt-automation', 
            'prompt', 
            '--dir', 'profile1', 
            '--content', 'profile2', 
            '--root_dir', self.test_dir
        ]
        with patch('sys.argv', test_args):
            with patch.object(PromptCommand, 'execute') as mock_execute:
                mock_execute.return_value = True
                main()
                mock_execute.assert_called_once()

    def test_root_dir_argument(self):
        with patch('sys.argv', ['gpt-automation', 'init', '--root_dir', self.test_dir]):
            with patch.object(InitCommand, 'execute') as mock_execute:
                mock_execute.return_value = True
                main()
                mock_execute.assert_called_once()

    def test_invalid_command(self):
        with patch('sys.argv', ['gpt-automation', 'invalid_command']):
            with self.assertRaises(SystemExit):
                main()

    def test_prompt_dir_argument(self):
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
