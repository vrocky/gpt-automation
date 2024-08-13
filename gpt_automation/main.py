import argparse
import os

from gpt_automation.arg_file_parser import ConfigurationLoader
from gpt_automation.setup_settings import SettingsSetup, SetupContext, PluginArguments
from gpt_automation.prompt_generator import PromptGenerator


class KeyValueAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for item in values:
            key, value = item.split('=')
            getattr(namespace, self.dest)[key] = value


def setup_cli_parser():
    """
    Sets up the command line interface parser with all the necessary subparsers and arguments.
    """
    parser = argparse.ArgumentParser(description="Automates project structure and file content generation.")
    parser.add_argument('--root_dir', default='.', help='Root directory for configuration.')
    parser.add_argument('--prompt_dir', default='.', help='Prompt directory to store generated content.')

    # Create subparsers for each command (init, prompt)
    subparsers = parser.add_subparsers(dest='command', required=True, help='Commands')

    # Setup 'init' command
    init_parser = subparsers.add_parser('init', help='Set up initial configuration files and directories.')
    init_parser.add_argument("profiles", nargs='*', default=[], help="Profile names for initial setup.")
    init_parser.add_argument('--args', nargs='*', action=KeyValueAction, help='Plugin arguments in key=value format')
    init_parser.add_argument('--arg_files', nargs='*', help='List of files containing plugin arguments')
    init_parser.add_argument('--config_files', nargs='*', help='Config files for different plugins (if any)')

    # Setup 'prompt' command
    prompt_parser = subparsers.add_parser('prompt', help='Generate structure and content prompts for profiles.')
    prompt_parser.add_argument("profiles", nargs='*', help="Profile names for generating prompts.")
    prompt_parser.add_argument("--dir", nargs='*', help="Generate directory structure for these profiles.")
    prompt_parser.add_argument("--content", nargs='*', help="Generate content for these profiles.")
    prompt_parser.add_argument('--args', nargs='*', action=KeyValueAction, help='Plugin arguments in key=value format')
    prompt_parser.add_argument('--arg_files', nargs='*', help='List of files containing plugin arguments')

    return parser


def parse_and_load_plugin_arguments(args):
    """
    Combines plugin arguments from command line and configuration files.
    """
    configuration_loader = ConfigurationLoader(args.arg_files)
    # Ensure cmd_args is always a dictionary
    cmd_args = getattr(args, 'args', {}) or {}
    combined_args = configuration_loader.merge_with_command_line(cmd_args)
    return PluginArguments(args=combined_args, config_file_args=args.config_files)


def main():
    """
    Main function to parse command line arguments and execute corresponding functionality.
    """
    parser = setup_cli_parser()
    args = parser.parse_args()

    if not is_valid_directory_structure(args.root_dir, args.prompt_dir):
        parser.error("'prompt_dir' must be a subdirectory of 'root_dir' or the same as 'root_dir'.")

    plugin_arguments = parse_and_load_plugin_arguments(args)

    setup_context = SetupContext(root_dir=args.root_dir, profile_names=args.profiles)

    if args.command == "init":
        config_creator = SettingsSetup(setup_context, plugin_arguments)
        config_creator.create_settings()
    elif args.command == "prompt":
        prompt_dir = args.prompt_dir
        prompt_generator = PromptGenerator(root_dir=setup_context.root_dir,
                                           prompt_dir=prompt_dir,
                                           conf_args=plugin_arguments.args,
                                           plugin_file_args=plugin_arguments.config_file_args)

        # Generate prompts based on the specified profiles and options
        prompt_generator.generate_prompt(
            dir_profiles=args.dir if args.dir else args.profiles,
            content_profiles=args.content if args.content else args.profiles,
            generate_dir=bool(args.dir),
            generate_content=bool(args.content)
        )
    else:
        # Display help if command is not recognized
        parser.print_help()


def is_valid_directory_structure(root_dir, prompt_dir):
    """ Validate that prompt_dir is a subdirectory of root_dir or the same. """
    relative_path = os.path.relpath(prompt_dir, root_dir)
    return relative_path == '.' or not relative_path.startswith('..')


if __name__ == "__main__":
    main()
