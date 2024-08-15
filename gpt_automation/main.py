import argparse
import os
import sys

from gpt_automation.prompt_manager import PromptManager
from gpt_automation.setup_settings import PluginArguments, SettingContext, SettingsSetup
from gpt_automation.utils.arg_file_parser import ConfigurationLoader

import argparse
import os
import sys
import argparse
import os
import sys

class KeyValueAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for item in values:
            key, value = item.split('=')
            getattr(namespace, self.dest)[key] = value

class RootLookup:
    def __init__(self, initial_dir):
        self.initial_dir = initial_dir

    def find_root_directory(self):
        """
        Recursively checks parent directories from the initial directory to find the '.gpt' directory.
        Returns the directory containing the '.gpt' directory as the root, if found.
        """
        current_dir = self.initial_dir
        while current_dir != os.path.dirname(current_dir):  # Stop when reaching the filesystem root
            if '.gpt' in os.listdir(current_dir):
                return current_dir
            current_dir = os.path.dirname(current_dir)
        return None

    def determine_directories(self, default_prompt_dir):
        """
        Determines the root and prompt directories based on the presence of the '.gpt' directory.
        """
        root_dir = self.find_root_directory()
        if root_dir:
            return root_dir, default_prompt_dir
        else:
            print("Error: No '.gpt' directory found in any parent directories.")
            sys.exit(1)

def setup_cli_parser():
    parser = argparse.ArgumentParser(description="Automates project structure and file content generation.")
    parser.add_argument('--root_dir', default=None, help='Root directory for configuration.')

    subparsers = parser.add_subparsers(dest='command', required=True, help='Commands')
    init_parser = subparsers.add_parser('init', help='Set up initial configuration files and directories.')
    init_parser.add_argument("profiles", nargs='*', default=[], help="Profile names for initial setup.")
    init_parser.add_argument('--args', nargs='*', action=KeyValueAction, help='Plugin arguments in key=value format')
    init_parser.add_argument('--arg_files', nargs='*', help='List of files containing plugin arguments')
    init_parser.add_argument('--config_files', nargs='*', help='Config files for different plugins (if any)')

    prompt_parser = subparsers.add_parser('prompt', help='Generate structure and content prompts for profiles.')
    prompt_parser.add_argument("profiles", nargs='*', help="Profile names for generating prompts.")
    prompt_parser.add_argument("--dir", nargs='*', default=None, help="Generate directory structure for these profiles.")
    prompt_parser.add_argument("--content", nargs='*', default=None, help="Generate content for these profiles.")
    prompt_parser.add_argument('--args', nargs='*', action=KeyValueAction, help='Plugin arguments in key=value format')
    prompt_parser.add_argument('--arg_files', nargs='*', help='List of files containing plugin arguments')
    prompt_parser.add_argument('--config_files', nargs='*', help='Config files for different plugins (if any)')
    prompt_parser.add_argument('--prompt_dir', default=None, help='Prompt directory to store generated content.')

    return parser

def handle_init(args):
    print(f"Root Directory: {os.path.abspath(args.root_dir)}")
    setup_context = SettingContext(root_dir=args.root_dir, profile_names=args.profiles)
    plugin_arguments = parse_and_load_plugin_arguments(args)
    config_creator = SettingsSetup(setup_context, plugin_arguments)
    config_creator.create_settings()

def handle_prompt(args):
    initial_dir = os.getcwd()
    root_lookup = RootLookup(initial_dir)
    root_dir, prompt_dir = root_lookup.determine_directories(args.prompt_dir or initial_dir)
    print(f"Root Directory: {root_dir}")
    print(f"Prompt Directory: {prompt_dir}")
    if not is_valid_directory_structure(root_dir, prompt_dir):
        print(f"Error: 'prompt_dir' {prompt_dir} must be a subdirectory of 'root_dir' {root_dir} or the same.")
        sys.exit(1)
    plugin_arguments = parse_and_load_plugin_arguments(args)
    prompt_generator = PromptManager(root_dir=root_dir, prompt_dir=prompt_dir, conf_args=plugin_arguments.args, plugin_file_args=plugin_arguments.config_file_args)
    generate_dir, generate_content, dir_profiles, content_profiles = determine_generation_options(args)
    prompt_generator.generate_prompt(dir_profiles=dir_profiles, content_profiles=content_profiles, generate_dir=generate_dir, generate_content=generate_content)

def main():
    parser = setup_cli_parser()
    args = parser.parse_args()

    if args.command == "init":
        handle_init(args)
    elif args.command == "prompt":
        handle_prompt(args)
    else:
        parser.print_help()

def parse_and_load_plugin_arguments(args):
    configuration_loader = ConfigurationLoader(args.arg_files)
    cmd_args = getattr(args, 'args', {}) or {}
    combined_args = configuration_loader.merge_with_command_line(cmd_args)
    return PluginArguments(args=combined_args, config_file_args=args.config_files)

def determine_generation_options(args):
    generate_dir = args.dir is not None
    generate_content = args.content is not None

    if not generate_dir and not generate_content:
        generate_dir = generate_content = True

    dir_profiles = args.dir if args.dir else args.profiles
    content_profiles = args.content if args.content else args.profiles

    return generate_dir, generate_content, dir_profiles, content_profiles

def is_valid_directory_structure(root_dir, prompt_dir):
    relative_path = os.path.relpath(prompt_dir, root_dir)
    return relative_path == '.' or not relative_path.startswith('..')

if __name__ == "__main__":
    main()
