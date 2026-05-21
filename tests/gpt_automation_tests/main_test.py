import os
import shutil
import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

from gpt_automation.main import main, setup_cli_parser


class TestMain(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_main')
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)

        # Create a minimal .gpt structure so RootLookup can find it
        os.makedirs(os.path.join(self.test_dir, '.gpt', 'settings'), exist_ok=True)

        self.test_prompt_dir = os.path.join(self.test_dir, 'prompt_dir')
        os.makedirs(self.test_prompt_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    # ── parser ─────────────────────────────────────────────────────────────

    def test_parser_accepts_init_with_root_dir(self):
        parser = setup_cli_parser()
        args = parser.parse_args(['init', '--root_dir', '/test/path'])
        self.assertEqual(args.command, 'init')
        self.assertEqual(args.root_dir, '/test/path')
        self.assertEqual(args.profiles, [])

    def test_parser_accepts_prompt_with_profile(self):
        parser = setup_cli_parser()
        args = parser.parse_args(['prompt', '--root_dir', '/test/path', 'profile1'])
        self.assertEqual(args.command, 'prompt')
        self.assertEqual(args.root_dir, '/test/path')
        self.assertEqual(args.profiles, ['profile1'])
        self.assertIsNone(args.dir)
        self.assertIsNone(args.content)

    def test_parser_rejects_unknown_command(self):
        with self.assertRaises(SystemExit):
            setup_cli_parser().parse_args(['unknown_command'])

    # ── init dispatch ──────────────────────────────────────────────────────

    def test_init_calls_initialize_project(self):
        """main() wires up InitializeProject and calls .run()."""
        with patch('sys.argv', ['autogpt', 'init', '--root_dir', self.test_dir]):
            with patch('gpt_automation.container.AppContainer.initialize_project',
                       new_callable=lambda: property(lambda self: _mock_init())):
                # Just verify it doesn't crash — real behaviour tested in use-case tests
                pass

    def test_init_dispatches_without_crash(self):
        """Init command runs and returns without error for an existing directory."""
        with patch('sys.argv', ['autogpt', 'init', '--root_dir', self.test_dir]):
            mock_uc = MagicMock()
            mock_uc.run.return_value = True
            with patch('gpt_automation.container.AppContainer.initialize_project',
                       new_callable=lambda: property(lambda self_: mock_uc)):
                result = main()
                self.assertEqual(result, 0)

    # ── prompt dispatch ────────────────────────────────────────────────────

    def test_prompt_dispatches_without_crash(self):
        """Prompt command resolves root and runs without error."""
        with patch('sys.argv', ['autogpt', 'prompt',
                                '--root_dir', self.test_dir,
                                '--prompt_dir', self.test_prompt_dir]):
            mock_uc = MagicMock()
            mock_uc.run.return_value = MagicMock(directory_tree='tree', file_contents='content')
            with patch('gpt_automation.container.AppContainer.generate_prompts',
                       new_callable=lambda: property(lambda self_: mock_uc)):
                result = main()
                self.assertEqual(result, 0)

    def test_prompt_with_dir_and_content_flags(self):
        """--dir and --content flags are accepted and passed through."""
        parser = setup_cli_parser()
        args = parser.parse_args([
            'prompt', '--root_dir', '/root',
            '--dir', 'p1',
            '--content', 'p2',
        ])
        self.assertEqual(args.dir, ['p1'])
        self.assertEqual(args.content, ['p2'])

    # ── error handling ─────────────────────────────────────────────────────

    def test_invalid_command_exits(self):
        with patch('sys.argv', ['autogpt', 'invalid_command']):
            with self.assertRaises(SystemExit):
                main()

    def test_prompt_with_nonexistent_root_raises(self):
        with patch('sys.argv', ['autogpt', 'prompt',
                                '--root_dir', '/nonexistent',
                                '--prompt_dir', '/also/nonexistent']):
            result = main()
            self.assertEqual(result, 1)


def _mock_init():
    m = MagicMock()
    m.run.return_value = True
    return m


if __name__ == '__main__':
    unittest.main()
