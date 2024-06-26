import os
import shutil


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