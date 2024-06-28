import os


class FilterManager:
    @staticmethod
    def merge_lists(paths):
        combined_list = []
        for path in paths:
            if os.path.exists(path):
                with open(path, 'r') as file:
                    combined_list.extend(file.read().strip().split('\n'))
        return list(set(combined_list))  # Remove duplicates and return

    @staticmethod
    def get_profile_paths(profile_names, file_name):
        if not profile_names:
            # Default to .gpt folder if no profiles are specified
            return [os.path.join(".gpt", file_name)]
        return [os.path.join(".gpt", "other_profiles", profile, file_name) for profile in profile_names]

    @staticmethod
    def get_global_filter_lists_for_profiles(profile_names=None):
        black_list_paths = FilterManager.get_profile_paths(profile_names, "black_list.txt")
        white_list_paths = FilterManager.get_profile_paths(profile_names, "white_list.txt")
        black_list = FilterManager.merge_lists(black_list_paths)
        white_list = FilterManager.merge_lists(white_list_paths)
        return black_list, white_list

    @staticmethod
    def validate_profile_initialization(profile_names):
        missing_profiles = []
        for profile_name in profile_names:
            profile_dir = os.path.join(".gpt", profile_name) if profile_name else ".gpt"
            black_list_file = os.path.join(profile_dir, "black_list.txt")
            white_list_file = os.path.join(profile_dir, "white_list.txt")
            if not (os.path.exists(black_list_file) and os.path.exists(white_list_file)):
                missing_profiles.append(profile_name)
        return missing_profiles
