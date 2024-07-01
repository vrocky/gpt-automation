import argparse

from gpt_automation.impl.config.config_manager import ConfigManager

from gpt_automation.prompt_generator import PromptGenerator
from gpt_automation.initializer import Initializer


def main():
    parser = argparse.ArgumentParser(
        description="Generate directory structure and file contents prompt for a GPT model.")
    subparsers = parser.add_subparsers(dest='command', help='Select a command to execute', required=True)

    init_parser = subparsers.add_parser('init',
                                        help='Initialize the .gpt directory with sample black and white list files.')
    init_parser.add_argument("profiles", nargs='*', default=[], help="Names of the profiles to initialize.")

    prompt_parser = subparsers.add_parser('prompt', help='Generate prompts for directory and/or file contents.')
    prompt_parser.add_argument("profiles", nargs='*', help="Profiles to generate prompts for.")
    prompt_parser.add_argument("--dir", nargs='*', default=None,
                               help="Generate directory structure prompt for these profiles.")
    prompt_parser.add_argument("--content", nargs='*', default=None,
                               help="Generate file contents prompt for these profiles.")

    args = parser.parse_args()

    if args.command == "init":
        dir_path = "."
        root_dir = dir_path
        initializer = Initializer(root_dir, args.profiles)
        initializer.initialize()

    elif args.command == "prompt":
        generate_dir = args.dir is not None
        generate_content = args.content is not None
        dir_path = "."

        prompt_generator = PromptGenerator(dir_path)

        # Combine all profile lists and remove duplicates using set
        all_profiles = set(args.profiles or [])
        dir_profiles = set(args.dir or [])
        content_profiles = set(args.content or [])

        # Combine all sets into one to ensure all profiles are unique
        combined_profiles = all_profiles | dir_profiles | content_profiles

        # Pass the combined and unique profiles to generate prompts
        if not generate_dir and not generate_content:
            generate_dir = generate_content = True  # Default to both if neither flag is provided

        prompt_generator.generate_prompt(dir_profiles=combined_profiles if generate_dir else set(),
                                         content_profiles=combined_profiles if generate_content else set(),
                                         generate_dir=generate_dir, generate_content=generate_content)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
