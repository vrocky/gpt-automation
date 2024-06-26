import argparse

from gpt_automation.config.config_manager import ConfigManager
from gpt_automation.profile_manager import init_profiles
from gpt_automation.prompt_generator import PromptGenerator

def main():
    parser = argparse.ArgumentParser(description="Generate directory structure and file contents prompt for a GPT model.")
    subparsers = parser.add_subparsers(dest='command', help='Select a command to execute', required=True)

    init_parser = subparsers.add_parser('init', help='Initialize the .gpt directory with sample black and white list files.')
    init_parser.add_argument("profiles", nargs='*', default=[], help="Names of the profiles to initialize.")

    prompt_parser = subparsers.add_parser('prompt', help='Generate prompts for directory and/or file contents.')
    prompt_parser.add_argument("profiles", nargs='*', help="Profiles to generate prompts for.")
    prompt_parser.add_argument("--dir", nargs='*', default=None, help="Generate directory structure prompt for these profiles.")
    prompt_parser.add_argument("--content", nargs='*', default=None, help="Generate file contents prompt for these profiles.")

    args = parser.parse_args()

    config_manager = ConfigManager()

    if args.command == "init":
        if not args.profiles:
            config_manager.initialize_configurations()  # Initialize default configurations
        else:
            for profile in args.profiles:
                config_manager.initialize_profile_config(profile)
    elif args.command == "prompt":
        prompt_generator = PromptGenerator(config_manager)
        generate_dir = args.dir is not None
        generate_content = args.content is not None
        both_profiles = args.profiles or []
        dir_profiles = args.dir if generate_dir else []
        content_profiles = args.content if generate_content else []

        # Default to both if neither flag is provided
        if not generate_dir and not generate_content:
            generate_dir = generate_content = True
            dir_profiles = content_profiles = []
        dir_profiles.extend(both_profiles)
        content_profiles.extend(both_profiles)

        prompt_generator.generate_prompt(dir_profiles=dir_profiles, content_profiles=content_profiles, generate_dir=generate_dir, generate_content=generate_content)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
