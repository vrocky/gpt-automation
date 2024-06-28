import os
import shutil
import fnmatch
from gpt_automation.impl.base_plugin import BasePlugin
from gpt_automation.impl.visitor.basevisitor import BaseVisitor


class BlacklistWhitelistPlugin(BasePlugin):
    def __init__(self, context, settings):
        super().__init__(context, settings)
        self.config_dir = context["plugin_settings_path"]
        self.profile_names = context.get("profile_names", [])

    def initialize(self, context):
        print("Initializing BlacklistWhitelistPlugin with context:", context)
        self.init_profiles(self.profile_names)

    def get_visitors(self):
        visitors = []
        for profile_name in self.profile_names:
            profile_path = self.get_profile_config_path(profile_name)
            blacklist, whitelist = self.load_filter_lists(profile_path)
            visitor = BlacklistWhitelistVisitor(blacklist, whitelist)
            visitors.append(visitor)
        return visitors

    def get_profile_config_path(self, profile_name):
        return os.path.join(self.config_dir, "profiles", profile_name)

    def load_filter_lists(self, profile_path):
        blacklist_path = os.path.join(profile_path, "black_list.txt")
        whitelist_path = os.path.join(profile_path, "white_list.txt")
        blacklist = self.read_list_from_file(blacklist_path)
        whitelist = self.read_list_from_file(whitelist_path)
        return blacklist, whitelist

    def read_list_from_file(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return file.read().strip().split('\n')
        return []

    def init_profiles(self, profile_names):
        sample_config_dir = os.path.join(os.path.dirname(__file__), "sample_config")
        for profile_name in profile_names:
            profile_dir = self.get_profile_config_path(profile_name)
            if not os.path.exists(profile_dir):
                os.makedirs(profile_dir)
                shutil.copyfile(os.path.join(sample_config_dir, "black_list.txt"),
                                os.path.join(profile_dir, "black_list.txt"))
                shutil.copyfile(os.path.join(sample_config_dir, "white_list.txt"),
                                os.path.join(profile_dir, "white_list.txt"))
                print(f"Initialized {profile_dir} folder with sample blacklist and whitelist files.")
            else:
                print(f"Profile {profile_name} already exists.")


class BlacklistWhitelistVisitor(BaseVisitor):
    def __init__(self, blacklist=None, whitelist=None):
        self.blacklist = blacklist or []
        self.whitelist = whitelist or []

    def enter_directory(self, directory_path):
        pass

    def leave_directory(self, directory_path):
        pass

    def should_visit_file(self, file_path):
        if any(fnmatch.fnmatch(file_path, pattern) for pattern in self.blacklist):
            return False
        return not self.whitelist or any(fnmatch.fnmatch(file_path, pattern) for pattern in self.whitelist)

    def should_visit_subdirectory(self, subdir_path):
        return self.should_visit_file(subdir_path)

    def before_traverse_directory(self, directory_path):
        print(f"Preparing to traverse {directory_path} with filters")

    def visit_file(self, file_path):
        print(f"Visiting file: {file_path}")
