import argparse
import os
import sys

from gpt_automation.prompt_manager import PromptManager
from gpt_automation.setup_settings import PluginArguments, SettingContext, SettingsSetup
from gpt_automation.utils.arg_file_parser import ConfigurationLoader
from gpt_automation.commands.init_command import InitCommand
from gpt_automation.commands.prompt_command import PromptCommand

class KeyValueAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for item in values:
            key, value = item.split('=')()
            getattr(namespace, self.dest)[key] = value

def setup_cli_parser():
    parser = argparse.ArgumentParser(description="Automates project structure and file content generation.")
    parser.add_argument('--root_dir', default=None, help='Root directory for configuration.')

    subparsers = parser.add_subparsers(dest='command', required=True, help='Commands')
    
    # Init command - simplified
    init_parser = subparsers.add_parser('init', help='Set up initial configuration files and directories.')
    init_parser.add_argument("profiles", nargs='*', default=[], help="Profile names for initial setup.")

    # Prompt command - simplified
    prompt_parser = subparsers.add_parser('prompt', help='Generate structure and content prompts for profiles.')
    prompt_parser.add_argument("profiles", nargs='*', help="Profile names for generating prompts.")
    prompt_parser.add_argument("--dir", nargs='*', default=None, help="Generate directory structure for these profiles.")
    prompt_parser.add_argument("--content", nargs='*', default=None, help="Generate content for these profiles.")
    prompt_parser.add_argument('--prompt_dir', default=None, help='Prompt directory to store generated content.')

    return parser

def main():
    parser = setup_cli_parser()
    args = parser.parse_args()

    root_dir = os.path.abspath(args.root_dir) if args.root_dir else os.getcwd()
    
    if args.command == "init":
        command = InitCommand(
            root_dir=root_dir,
            profile_names=args.profiles
        )
        command.execute()
        
    elif args.command == "prompt":
        generate_dir = args.dir is not None
        generate_content = args.content is not None
        if not generate_dir and not generate_content:
            generate_dir = generate_content = True
            
        dir_profiles = args.dir if args.dir else args.profiles
        content_profiles = args.content if args.content else args.profiles
        
        command = PromptCommand(
            root_dir=root_dir,
            prompt_dir=args.prompt_dir or root_dir,
            profiles=args.profiles,
            dir_profiles=dir_profiles,
            content_profiles=content_profiles,
            generate_dir=generate_dir,
            generate_content=generate_content
        )
        command.execute()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
