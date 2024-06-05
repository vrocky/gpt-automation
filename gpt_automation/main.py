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
        # Default to .gpt folder if no profiles are specified
        return [os.path.join(".gpt", file_name)]
    return [os.path.join(".gpt", "other_profiles", profile, file_name) for profile in profile_names]


def get_global_filter_lists_for_profiles(profile_names=None):

    black_list_paths = get_profile_paths(profile_names, "black_list.txt")
    white_list_paths = get_profile_paths(profile_names, "white_list.txt")
    black_list = merge_lists(black_list_paths)
    white_list = merge_lists(white_list_paths)
    return black_list, white_list


def validate_profile_initialization(profile_names):
    missing_profiles = []
    for profile_name in profile_names:
        profile_dir = os.path.join(".gpt", profile_name) if profile_name else ".gpt"
        black_list_file = os.path.join(profile_dir, "black_list.txt")
        white_list_file = os.path.join(profile_dir, "white_list.txt")
        if not (os.path.exists(black_list_file) and os.path.exists(white_list_file)):
            missing_profiles.append(profile_name)
    return missing_profiles


def generate_prompt(project_path='.', dir_profiles=None, content_profiles=None, generate_dir=False, generate_content=False):
    all_profiles = set(dir_profiles or []) | set(content_profiles or [])
    missing_profiles = validate_profile_initialization(all_profiles)
    if missing_profiles:
        missing_profiles_str = ", ".join(missing_profiles)
        print(f"Warning: The following profiles are not properly initialized: {missing_profiles_str}.")
        return  # Exit if there are missing profiles

    dir_prompt = ""
    content_prompt = ""
    content_prompt_dir_preview = ""

    if generate_dir:
        dir_black_list, dir_white_list = get_global_filter_lists_for_profiles(dir_profiles)
        dir_prompt = create_directory_prompt(project_path, dir_black_list, dir_white_list,dir_profiles)

    if generate_content:
        content_black_list, content_white_list = get_global_filter_lists_for_profiles(content_profiles)
        content_prompt_dir_preview = create_directory_prompt(project_path, content_black_list, content_white_list,content_profiles)
        content_prompt = create_content_prompt(project_path, content_black_list, content_white_list,content_profiles)

    if dir_prompt:
        print("\nDirectory Structure Preview:")
        print(dir_prompt)

    if content_prompt_dir_preview:
        print("\nDirectory Preview for Content (to indicate what has been copied):")
        print(content_prompt_dir_preview)

    combined_prompt = ""
    if dir_prompt:
        combined_prompt += "Directory Structure:\n" + f"{dir_prompt}\n"
    if content_prompt:
        combined_prompt += "File Contents:\n" + f"{content_prompt}".strip()
    if combined_prompt:
        pyperclip.copy(combined_prompt)
        if dir_prompt and content_prompt:
            print("\nBoth directory structure and file contents have been copied to the clipboard.")
        elif dir_prompt:
            print("\nDirectory structure prompt has been copied to the clipboard.")
        elif content_prompt:
            print("\nFile contents prompt has been copied to the clipboard.")




def create_directory_prompt(project_path, black_list, white_list, profile_names):
    project_info = ProjectInfo(project_path, black_list, white_list, profile_names)

    return project_info.create_directory_structure_prompt()


def create_content_prompt(project_path, black_list, white_list, profile_names):
    project_info = ProjectInfo(project_path, black_list, white_list, profile_names)
    return project_info.create_file_contents_prompt()



def init_profiles(profile_names):
    if not profile_names:
        profile_names = ['']  # Placeholder for the default profile when profile_names is empty
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
        else:
            print(f"Profile {profile_name} already exists.")



def main():
    parser = argparse.ArgumentParser(description="Generate directory structure and file contents prompt for a GPT model.")
    subparsers = parser.add_subparsers(dest='command', help='Select a command to execute', required=True)

    init_parser = subparsers.add_parser('init', help='Initialize the .gpt directory with sample black and white list files.')
    init_parser.add_argument("profiles", nargs='*', default=[], help="Names of the profiles to initialize.")

    prompt_parser = subparsers.add_parser('prompt', help='Generate prompts for directory and/or file contents.')
    prompt_parser.add_argument("profiles", nargs='*', help="Profiles to generate prompts for.")
    prompt_parser.add_argument("--dir", nargs='*', default=None, help="Generate directory structure prompt for these profiles.")
    prompt_parser.add_argument("--content", nargs='*', default=None, help="Generate file contents prompt for these profiles.")

    args, unknown = parser.parse_known_args()
    if unknown:
        print("Unknown arguments:", unknown)

    if args.command == "init":
        init_profiles(args.profiles)
    elif args.command == "prompt":
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
        generate_prompt('.', dir_profiles, content_profiles, generate_dir, generate_content)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()