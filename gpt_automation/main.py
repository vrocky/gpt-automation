import argparse

from gpt_automation.setup_settings import SettingsSetup
from gpt_automation.prompt_generator import PromptGenerator


def setup_cli_parser():
    """
    Sets up the command line interface parser with all the necessary subparsers and arguments.

    Returns:
        argparse.ArgumentParser: Configured parser with all commands and options.
    """
    parser = argparse.ArgumentParser(description="Automates project structure and file content generation.")

    # Create subparsers for each command (init, prompt)
    subparsers = parser.add_subparsers(dest='command', required=True, help='Commands')

    # Setup 'init' command to initialize configuration files and directories
    init_parser = subparsers.add_parser('init', help='Set up initial configuration files and directories.')
    init_parser.add_argument("profiles", nargs='*', default=[], help="Profile names for initial setup.")

    # Setup 'prompt' command to generate structure and content prompts
    prompt_parser = subparsers.add_parser('prompt', help='Generate structure and content prompts for profiles.')
    prompt_parser.add_argument("profiles", nargs='*', help="Profile names for generating prompts.")
    prompt_parser.add_argument("--dir", nargs='*', help="Generate directory structure for these profiles.")
    prompt_parser.add_argument("--content", nargs='*', help="Generate content for these profiles.")

    return parser


def main():
    """
    Main function to parse command line arguments and execute corresponding functionality.
    """
    parser = setup_cli_parser()
    args = parser.parse_args()

    # Directory where the configuration is to be created or used
    settings_dir = "."

    # Execute based on the command specified
    if args.command == "init":
        # Initialize profiles using the ConfigCreator
        config_creator = SettingsSetup(settings_dir, args.profiles, plugin_args=[], plugin_file_args=[])
        config_creator.create_settings()
    elif args.command == "prompt":
        # Initialize the PromptGenerator with the configuration directory
        prompt_generator = PromptGenerator(settings_dir,plugin_args=[],plugin_file_args=[])

        # Check if specific options for directory or content generation are provided
        if args.dir or args.content:
            # Set directory profiles to the ones specified in --dir or default to general profiles
            dir_profiles = args.dir if args.dir else args.profiles
            # Set content profiles to the ones specified in --content or default to general profiles
            content_profiles = args.content if args.content else args.profiles

            # Generate prompts based on the specified profiles
            # `generate_dir` is True if --dir is explicitly mentioned,
            # indicating the intention to generate directory prompts
            # `generate_content` is True if --content is explicitly mentioned,
            # indicating the intention to generate content prompts
            prompt_generator.generate_prompt(
                dir_profiles=dir_profiles,
                content_profiles=content_profiles,
                generate_dir=bool(args.dir),
                generate_content=bool(args.content)
            )
        else:
            # If no specific flags are provided, use the profiles for both directory and content generation
            # This defaults to generating both directory and content prompts for the specified profiles
            prompt_generator.generate_prompt(
                dir_profiles=args.profiles,
                content_profiles=args.profiles,
                generate_dir=True,
                generate_content=True
            )
    else:
        # Display help if command is not recognized
        parser.print_help()


if __name__ == "__main__":
    main()
