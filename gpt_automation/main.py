import shutil
import sys
import argparse
import os
import pyperclip
from gpt_automation.project_info import ProjectInfo


def merge_lists(paths):
    combined_list = []
    for path in paths:
        if os.path.exists(path):
            with open(path, 'r') as file:
                combined_list.extend(file.read().strip().split('\n'))
    return list(set(combined_list))  # Remove duplicates and return


def get_profile_paths(profile_names, file_name):
    if not profile_names:
        return [os.path.join(".gpt", file_name)]  # Default to .gpt folder if no profiles are specified
    return [os.path.join(".gpt", "other_profiles", profile, file_name) for profile in profile_names]


def get_global_filter_lists_for_profiles(profile_names):
    black_list_paths = get_profile_paths(profile_names, "black_list.txt")
    white_list_paths = get_profile_paths(profile_names, "white_list.txt")
    black_list = merge_lists(black_list_paths)
    white_list = merge_lists(white_list_paths)
    return black_list, white_list


def generate_prompt(project_path='.', dir_profiles=None, content_profiles=None):
    if dir_profiles is not None:
        dir_black_list, dir_white_list = get_global_filter_lists_for_profiles(dir_profiles)
        dir_prompt = create_directory_prompt(project_path, dir_black_list, dir_white_list, profile_names=dir_profiles)
    else:
        dir_prompt = ""
    content_prompt_dir_preview = ""
    if content_profiles is not None:

        content_black_list, content_white_list = get_global_filter_lists_for_profiles(content_profiles)
        content_prompt_dir_preview = create_directory_prompt(project_path, content_black_list, content_white_list,
                                                 profile_names=content_profiles)

        content_prompt = create_content_prompt(project_path, content_black_list, content_white_list,
                                               profile_names=content_profiles)
    else:
        content_prompt = ""

    print("\nDirectory Structure Preview:")
    print(dir_prompt)  # Displays the generated directory structure based on the provided profiles

    print("\nSelected Files for Content Inclusion:")
    print(content_prompt_dir_preview)  # Shows a list of selected files whose content will be included in the prompt

    combined_prompt = "Directory Structure:\n" + f"{dir_prompt}\nFile Contents:\n{content_prompt}".strip()
    pyperclip.copy(combined_prompt)  # Copies the combined directory structure and file content prompts to the clipboard
    print("\nCombined directory structure and selected file content prompt has been copied to the clipboard.")




def create_directory_prompt(project_path, black_list, white_list, profile_names):
    project_info = ProjectInfo(project_path, black_list, white_list, profile_names)

    return  project_info.create_directory_structure_prompt()


def create_content_prompt(project_path, black_list, white_list, profile_names):
    project_info = ProjectInfo(project_path, black_list, white_list, profile_names)
    return project_info.create_file_contents_prompt()


def init_profiles(profile_names):
    if not profile_names:
        profile_names = [""]  # Default to .gpt folder if no profiles are specified
    for profile_name in profile_names:
        profile_dir = os.path.join(".gpt", profile_name) if profile_name else ".gpt"
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
        sample_black_list_path = os.path.join(os.path.dirname(__file__), "sample_config/black_list.txt")
        sample_white_list_path = os.path.join(os.path.dirname(__file__), "sample_config/white_list.txt")
        target_black_list_path = os.path.join(profile_dir, "black_list.txt")
        target_white_list_path = os.path.join(profile_dir, "white_list.txt")
        shutil.copyfile(sample_black_list_path, target_black_list_path)
        shutil.copyfile(sample_white_list_path, target_white_list_path)
        print(f"Initialized {profile_dir} folder with sample black_list.txt and white_list.txt files.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate directory structure and file contents prompt for a GPT model.")
    subparsers = parser.add_subparsers(dest='command', help='Select a command to execute')

    init_parser = subparsers.add_parser('init',
                                        help='Initialize the .gpt directory with sample black and white list files.')
    init_parser.add_argument("profiles", nargs='*', default=[], help="Names of the profiles to initialize.")

    prompt_parser = subparsers.add_parser('prompt', help='Generate prompts for directory and/or file contents.')
    prompt_parser.add_argument("--dir", nargs='*', default=None,
                               help="Generate directory structure prompt for these profiles.")
    prompt_parser.add_argument("--content", nargs='*', default=None,
                               help="Generate file contents prompt for these profiles.")

    args = parser.parse_args()
    if args.command == "init":
        init_profiles(args.profiles)
    elif args.command == "prompt":
        generate_prompt('.', dir_profiles=args.dir, content_profiles=args.content)


if __name__ == "__main__":
    main()
