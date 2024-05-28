# gpt_automation\main.py
import shutil
import sys

import pyperclip
import argparse
import os
from gpt_automation.project_info import ProjectInfo


import shutil
import sys

import pyperclip
import argparse
import os
from gpt_automation.project_info import ProjectInfo


def prompt_all(project_path='.', profile_name=None):
    profile_dir = f".gpt/other_profiles/{profile_name}" if profile_name else ".gpt"

    black_list_file = os.path.join(profile_dir, "black_list.txt")
    white_list_file = os.path.join(profile_dir, "white_list.txt")

    with open(black_list_file, 'r') as f:
        black_list = f.read()

    with open(white_list_file, 'r') as f:
        white_list = f.read()

    project_info = ProjectInfo(project_path, black_list, white_list, profile_name)

    directory_structure_prompt = project_info.create_directory_structure_prompt()
    print(directory_structure_prompt)

    file_contents_prompt = project_info.create_file_contents_prompt()

    single_prompt = directory_structure_prompt + '\n' + file_contents_prompt

    # Copy the prompt to the clipboard
    pyperclip.copy(single_prompt)

    print("Prompt copied to clipboard.")


def prompt_only_dir_structure(project_path='.', profile_name=None):
    profile_dir = f".gpt/other_profiles/{profile_name}" if profile_name else ".gpt"

    black_list_file = os.path.join(profile_dir, "black_list.txt")
    white_list_file = os.path.join(profile_dir, "white_list.txt")

    with open(black_list_file, 'r') as f:
        black_list = f.read()

    with open(white_list_file, 'r') as f:
        white_list = f.read()

    project_info = ProjectInfo(project_path, black_list, white_list,profile_name)

    directory_structure_prompt = project_info.create_directory_structure_prompt()
    print(directory_structure_prompt)

    # Copy the prompt to the clipboard
    pyperclip.copy(directory_structure_prompt)

    print("Prompt for directory structure copied to clipboard.")

def init_gql_folder(profile_name=None):
    # Use the profile name to determine the folder to initialize
    profile_dir = f".gpt/other_profiles/{profile_name}" if profile_name else ".gpt"

    # Create .gpt directory or profile directory if it doesn't exist
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)

    # Copy sample black_list.txt and white_list.txt to .gql directory
    sample_black_list_path = os.path.join(os.path.dirname(__file__), "sample_config/black_list.txt")
    sample_white_list_path = os.path.join(os.path.dirname(__file__), "sample_config/white_list.txt")

    target_black_list_path = os.path.join(profile_dir, "black_list.txt")
    target_white_list_path = os.path.join(profile_dir, "white_list.txt")

    if not os.path.exists(target_black_list_path):
        shutil.copyfile(sample_black_list_path, target_black_list_path)

    if not os.path.exists(target_white_list_path):
        shutil.copyfile(sample_white_list_path, target_white_list_path)

    print(f"Initialized {profile_dir} folder with sample black_list.txt and white_list.txt files.")

def main():
    parser = argparse.ArgumentParser(
        description="Generate directory structure and file contents prompt for a GPT model.",
    )

    subparsers = parser.add_subparsers(dest='command', help='Select a command to execute')

    init_parser = subparsers.add_parser('init',
                                        help='Initialize the .gpt directory with sample black and white list files.')
    init_parser.add_argument("--profile", default=None,
                             help="Name of the profile to initialize (default: default profile).")

    prompt_all_parser = subparsers.add_parser('prompt-all',
                                              help='Create a directory structure and file contents prompt.')
    prompt_all_parser.add_argument("--path", default=".",
                                   help="Path to your project's root directory (default: current directory). "
                                        "The tool will start traversing the directory structure from here.")
    prompt_all_parser.add_argument("--profile", default=None,
                                   help="Name of the profile to use (default: default profile).")

    prompt_dir_parser = subparsers.add_parser('prompt-dir',
                                              help='Create a directory structure prompt without file contents.')
    prompt_dir_parser.add_argument("--path", default=".",
                                   help="Path to your project's root directory (default: current directory). "
                                        "The tool will start traversing the directory structure from here.")
    prompt_dir_parser.add_argument("--profile", default=None,
                                   help="Name of the profile to use (default: default profile).")

    args = parser.parse_args()

    # Check if no arguments were passed and display help message
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.command == "init":
        init_gql_folder(args.profile)
    elif args.command == "prompt-all":
        path = args.path
        prompt_all(path, args.profile)
    elif args.command == "prompt-dir":
        path = args.path
        prompt_only_dir_structure(path, args.profile)


if __name__ == "__main__":
    main()

