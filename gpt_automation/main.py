# gpt_automation\main.py
import shutil
import sys
import argparse
import os
import pyperclip
from gpt_automation.project_info import ProjectInfo

def prompt_all(project_path='.', profile_names=None):
    profile_dir = f".gpt/other_profiles/{','.join(profile_names)}" if profile_names else ".gpt"

    black_list_file = os.path.join(profile_dir, "black_list.txt")
    white_list_file = os.path.join(profile_dir, "white_list.txt")

    black_list = open(black_list_file, 'r').read() if os.path.exists(black_list_file) else ""
    white_list = open(white_list_file, 'r').read() if os.path.exists(white_list_file) else ""

    project_info = ProjectInfo(project_path, black_list, white_list, profile_names)
    directory_structure_prompt = project_info.create_directory_structure_prompt()
    file_contents_prompt = project_info.create_file_contents_prompt()

    single_prompt = f"{directory_structure_prompt}\n{file_contents_prompt}"
    print(directory_structure_prompt)
    pyperclip.copy(single_prompt)
    print("Prompt copied to clipboard.")

def prompt_only_dir_structure(project_path='.', profile_names=None):
    profile_dir = f".gpt/other_profiles/{','.join(profile_names)}" if profile_names else ".gpt"

    black_list_file = os.path.join(profile_dir, "black_list.txt")
    white_list_file = os.path.join(profile_dir, "white_list.txt")

    black_list = open(black_list_file, 'r').read() if os.path.exists(black_list_file) else ""
    white_list = open(white_list_file, 'r').read() if os.path.exists(white_list_file) else ""

    project_info = ProjectInfo(project_path, black_list, white_list, profile_names)
    directory_structure_prompt = project_info.create_directory_structure_prompt()

    print(directory_structure_prompt)
    pyperclip.copy(directory_structure_prompt)
    print("Prompt for directory structure copied to clipboard.")

def init_gql_folder(profile_names=None):
    profile_dir = f".gpt/other_profiles/{','.join(profile_names)}" if profile_names else ".gpt"
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)

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
    parser = argparse.ArgumentParser(description="Generate directory structure and file contents prompt for a GPT model.")
    subparsers = parser.add_subparsers(dest='command', help='Select a command to execute')

    init_parser = subparsers.add_parser('init', help='Initialize the .gpt directory with sample black and white list files.')
    init_parser.add_argument("--profiles", nargs='+', default=[], help="Names of the profiles to initialize.")

    prompt_all_parser = subparsers.add_parser('prompt-all', help='Create a directory structure and file contents prompt.')
    prompt_all_parser.add_argument("--path", default=".", help="Path to your project's root directory.")
    prompt_all_parser.add_argument("--profiles", nargs='+', default=[], help="Names of the profiles to use.")

    prompt_dir_parser = subparsers.add_parser('prompt-dir', help='Create a directory structure prompt without file contents.')
    prompt_dir_parser.add_argument("--path", default=".", help="Path to your project's root directory.")
    prompt_dir_parser.add_argument("--profiles", nargs='+', default=[], help="Names of the profiles to use.")

    args = parser.parse_args()
    if args.command == "init":
        init_gql_folder(args.profiles)
    elif args.command == "prompt-all":
        prompt_all(args.path, args.profiles)
    elif args.command == "prompt-dir":
        prompt_only_dir_structure(args.path, args.profiles)

if __name__ == "__main__":
    main()
