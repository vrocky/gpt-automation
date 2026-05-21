"""
Application entry point.

Parses CLI arguments, resolves the project root, builds the dependency
container, and dispatches to the right use case.

Nothing complex happens here — all logic lives in the application layer.
"""

import argparse
import sys
from pathlib import Path

from gpt_automation.container import AppContainer
from gpt_automation.infrastructure.filesystem.root_discovery import RootLookup


def _build_parser() -> argparse.ArgumentParser:
    """Declare every CLI argument in one place."""
    parser = argparse.ArgumentParser(
        prog='autogpt',
        description='Automate GPT-friendly project documentation.',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # ── init ──────────────────────────────────────────────────────────
    init = subparsers.add_parser('init', help='Set up a project with .gpt/ directory and settings.')
    init.add_argument('--root_dir', default=None, metavar='DIR',
                      help='Project root (defaults to current directory).')
    init.add_argument('profiles', nargs='*', default=[],
                      help='Optional profile names to initialise.')

    # ── prompt ────────────────────────────────────────────────────────
    prompt = subparsers.add_parser('prompt', help='Generate directory-structure / file-content prompts.')
    prompt.add_argument('--root_dir', default=None, metavar='DIR',
                        help='Project root (auto-discovered if omitted).')
    prompt.add_argument('--prompt_dir', default=None, metavar='DIR',
                        help='Directory to analyse (defaults to current directory).')
    prompt.add_argument('profiles', nargs='*', default=[],
                        help='Default profiles for both tree and content.')
    prompt.add_argument('--dir', nargs='*', default=None, metavar='PROFILE',
                        help='Generate directory tree (optional profile override).')
    prompt.add_argument('--content', nargs='*', default=None, metavar='PROFILE',
                        help='Generate file content (optional profile override).')

    return parser


def main() -> int:
    """Entry point. Returns exit code (0 = success)."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == 'init':
        return _run_init(args)

    if args.command == 'prompt':
        return _run_prompt(args)

    parser.print_help()
    return 1


def _run_init(args) -> int:
    """Dispatch init command through the container."""
    root = Path(args.root_dir).resolve() if args.root_dir else Path.cwd()
    container = AppContainer(root)
    success = container.initialize_project.run(args.profiles)
    return 0 if success else 1


def _run_prompt(args) -> int:
    """Dispatch prompt command through the container."""
    # Discover root directory (walk up from cwd looking for .gpt/)
    lookup = RootLookup(
        initial_dir=args.root_dir or str(Path.cwd()),
        provided_root_dir=args.root_dir,
    )
    try:
        root_str, work_str = lookup.determine_directories(args.prompt_dir)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    root = Path(root_str)
    work = Path(work_str)

    container = AppContainer(root)

    # Decide what to generate
    want_tree = args.dir is not None
    want_content = args.content is not None
    if not want_tree and not want_content:
        want_tree = want_content = True

    dir_profiles = args.dir if args.dir else args.profiles
    content_profiles = args.content if args.content else args.profiles

    # Generate tree
    if want_tree:
        result = container.generate_prompts.run(
            work_dir=work,
            profiles=dir_profiles,
            include_tree=True,
            include_contents=False,
        )
        if result.directory_tree:
            _send_to_clipboard(result.directory_tree)
            print("Directory tree copied to clipboard.")

    # Generate content
    if want_content:
        result = container.generate_prompts.run(
            work_dir=work,
            profiles=content_profiles,
            include_tree=False,
            include_contents=True,
        )
        if result.file_contents:
            _send_to_clipboard(result.file_contents)
            print("File contents copied to clipboard.")

    return 0


def _send_to_clipboard(text: str) -> None:
    """Copy text to system clipboard, silently ignore if unavailable."""
    try:
        import pyperclip
        pyperclip.copy(text)
    except Exception:
        print(text)  # Fall back to stdout


# Public alias kept for test compatibility
setup_cli_parser = _build_parser

if __name__ == '__main__':
    sys.exit(main())
