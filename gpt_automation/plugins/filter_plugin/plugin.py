import os
import shutil
import fnmatch
from gpt_automation.impl.base_plugin import BasePlugin
from gpt_automation.impl.visitor.basevisitor import BaseVisitor


class BlacklistWhitelistPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.config_dir = None
        self.root_dir = None
        self.profile_names = None
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        self.sample_config_dir = os.path.join(self.plugin_dir, "sample_config")

    def init(self, plugin_settings_path: str, root_dir: str, profile_names: list):
        """Initialize plugin with all required parameters"""
        self.plugin_settings_path = plugin_settings_path
        self.config_dir = plugin_settings_path
        self.configure(root_dir, profile_names)

    def configure(self, root_dir, profile_names):
        """Initialize plugin configuration"""
        self.root_dir = root_dir
        self.profile_names = profile_names

        
        # Initialize default configuration
        self.init_default_config()
        
        # Configure profiles if any
        if profile_names:
            self.configure_profiles(profile_names)

    def is_plugin_configured(self):
        """Check if plugin is properly configured"""
        try:
            if not self.config_dir:
                return False
                
            # Check default configuration
            default_blacklist = os.path.join(self.config_dir, "black_list.txt")
            default_whitelist = os.path.join(self.config_dir, "white_list.txt")
            
            if not (os.path.exists(default_blacklist) and os.path.exists(default_whitelist)):
                return False

            # Check profile configurations if profiles exist
            if self.profile_names:
                for profile_name in self.profile_names:
                    profile_dir = os.path.join(self.config_dir, profile_name)
                    blacklist_path = os.path.join(profile_dir, "black_list.txt")
                    whitelist_path = os.path.join(profile_dir, "white_list.txt")
                    if not (os.path.exists(blacklist_path) and os.path.exists(whitelist_path)):
                        return False

            return True
            
        except Exception as e:
            print(f"Error checking plugin configuration: {str(e)}")
            return False

    def get_visitors(self,prompt_dir):
        visitors = []

        if not self.profile_names:  # If no profiles specified, use default configuration
            blacklist, whitelist = self.load_filter_lists(self.config_dir)
            visitors.append(BlacklistWhitelistVisitor(blacklist, whitelist))
        else:
            for profile_name in self.profile_names:
                profile_path = self.get_profile_config_path(profile_name)
                blacklist, whitelist = self.load_filter_lists(profile_path)
                visitors.append(BlacklistWhitelistVisitor(blacklist, whitelist))
        print("visitors",visitors)
        return visitors

    def init_default_config(self):
        """Initialize default configuration files"""
        try:
            print("self.config_dir", self.config_dir)   
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)


            default_blacklist = os.path.join(self.config_dir, "black_list.txt")
            default_whitelist = os.path.join(self.config_dir, "white_list.txt")

            if not os.path.exists(default_blacklist):
                shutil.copyfile(
                    os.path.join(self.sample_config_dir, "black_list.txt"),
                    default_blacklist
                )
            if not os.path.exists(default_whitelist):
                shutil.copyfile(
                    os.path.join(self.sample_config_dir, "white_list.txt"),
                    default_whitelist
                )
        except Exception as e:
            print(f"Error initializing default configuration: {str(e)}")

    def configure_profiles(self, profile_names):
        """Configure profiles with their own blacklist and whitelist"""
        for profile_name in profile_names:
            profile_dir = os.path.join(self.config_dir, profile_name)
            try:
                if not os.path.exists(profile_dir):
                    os.makedirs(profile_dir)
                    shutil.copyfile(
                        os.path.join(self.sample_config_dir, "black_list.txt"),
                        os.path.join(profile_dir, "black_list.txt")
                    )
                    shutil.copyfile(
                        os.path.join(self.sample_config_dir, "white_list.txt"),
                        os.path.join(profile_dir, "white_list.txt")
                    )
                    print(f"Initialized {profile_dir} with sample blacklist and whitelist files.")
            except Exception as e:
                print(f"Error configuring profile {profile_name}: {str(e)}")

    def get_profile_config_path(self, profile_name):
        return os.path.join(self.config_dir, profile_name)

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
        if any(fnmatch.fnmatch(subdir_path, pattern) for pattern in self.blacklist):
            return False
        return True

    def before_traverse_directory(self, directory_path):
        print(f"Preparing to traverse {directory_path} with filters")

    def visit_file(self, file_path):
        pass
        #print(f"Visiting file: {file_path}")
