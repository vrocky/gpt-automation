import shutil
import pyperclip
import argparse
import os
from gpt_automation.project_info import ProjectInfo


def prompt_all(project_path, black_list_file, white_list_file):
    with open(black_list_file, 'r') as f:
        black_list = f.read()

    with open(white_list_file, 'r') as f:
        white_list = f.read()

    project_info = ProjectInfo(project_path, black_list, white_list)

    directory_structure_prompt = project_info.create_directory_structure_prompt()
    print(directory_structure_prompt)

    file_contents_prompt = project_info.create_file_contents_prompt()

    single_prompt = directory_structure_prompt + '\n' + file_contents_prompt

    # Copy the prompt to the clipboard
    pyperclip.copy(single_prompt)

    print("Prompt copied to clipboard.")


def prompt_only_dir_structure(project_path, black_list_file, white_list_file):
    with open(black_list_file, 'r') as f:
        black_list = f.read()

    with open(white_list_file, 'r') as f:
        white_list = f.read()

    project_info = ProjectInfo(project_path, black_list, white_list)

    directory_structure_prompt = project_info.create_directory_structure_prompt()
    print(directory_structure_prompt)

    # Copy the prompt to the clipboard
    pyperclip.copy(directory_structure_prompt)

    print("Prompt for directory structure copied to clipboard.")


def init_gql_folder():
    # Create .gql directory if it doesn't exist
    if not os.path.exists(".gpt"):
        os.makedirs(".gpt")

    # Copy sample black_list.txt and white_list.txt to .gql directory
    sample_black_list_path = os.path.join(os.path.dirname(__file__), "sample_config/black_list.txt")
    sample_white_list_path = os.path.join(os.path.dirname(__file__), "sample_config/white_list.txt")

    target_black_list_path = os.path.join(".gpt", "black_list.txt")
    target_white_list_path = os.path.join(".gpt", "white_list.txt")

    if not os.path.exists(target_black_list_path):
        shutil.copyfile(sample_black_list_path, target_black_list_path)

    if not os.path.exists(target_white_list_path):
        shutil.copyfile(sample_white_list_path, target_white_list_path)

    print("Initialized .gpt folder with sample black_list.txt and white_list.txt files.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate directory structure and file contents prompt for a GPT model.",
    )

    subparsers = parser.add_subparsers(dest='command', help='Select a command to execute')

    init_parser = subparsers.add_parser('init',
                                        help='Initialize the .gpt directory with sample black and white list files.')

    prompt_all_parser = subparsers.add_parser('prompt-all',
                                              help='Create a directory structure and file contents prompt.')
    prompt_all_parser.add_argument("--black-list-file", default=".gpt/black_list.txt",
                                   help="Path to the black list file (default: .gpt/black_list.txt). "
                                        "This file should contain patterns for files and directories to ignore.")
    prompt_all_parser.add_argument("--white-list-file", default=".gpt/white_list.txt",
                                   help="Path to the white list file (default: .gpt/white_list.txt). "
                                        "This file should contain patterns for files to include. "
                                        "If a white list is provided, only files matching these patterns will be included.")
    prompt_all_parser.add_argument("--project-path", default=".",
                                   help="Path to your project's root directory (default: current directory). "
                                        "The tool will start traversing the directory structure from here.")

    prompt_dir_parser = subparsers.add_parser('prompt-dir',
                                              help='Create a directory structure prompt without file contents.')
    prompt_dir_parser.add_argument("--black-list-file", default=".gpt/black_list.txt",
                                   help="Path to the black list file (default: .gpt/black_list.txt). "
                                        "This file should contain patterns for directories to ignore.")
    prompt_dir_parser.add_argument("--white-list-file", default=".gpt/white_list.txt",
                                   help="Path to the white list file (default: .gpt/white_list.txt). "
                                        "This file should contain patterns for directories to include. "
                                        "If a white list is provided, only directories matching these patterns will be included.")
    prompt_dir_parser.add_argument("--project-path", default=".",
                                   help="Path to your project's root directory (default: current directory). "
                                        "The tool will start traversing the directory structure from here.")

    args = parser.parse_args()

    if args.command == "init":
        init_gql_folder()
    elif args.command == "prompt-all":
        project_path = args.project_path
        prompt_all(project_path, args.black_list_file, args.white_list_file)
    elif args.command == "prompt-dir":
        project_path = args.project_path
        prompt_only_dir_structure(project_path, args.black_list_file, args.white_list_file)


if __name__ == "__main__":
    main()
