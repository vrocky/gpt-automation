from gpt_automation.impl.app import App


class AppContext:
    def __init__(self, root_dir, profile_names, conf_args, plugin_file_args):
        self.app = App(root_dir, profile_names, conf_args, plugin_file_args)

    def get_path_manager(self):
        return self.app.path_manager

    def get_config_manager(self):
        return self.app.settings_manager

    def get_plugin_manager(self):
        return self.app.plugin_manager

    def get_directory_walker(self):
        return self.app.directory_walker  # Access the directory walker through the app

    def get_root_dir(self):
        return self.app.root_dir

    def create_profiles(self):
        return self.app.create_profiles()

    def check_profile_created(self):
        return self.app.check_profiles_created()

    def load_plugins(self):
        return self.app.load_plugins()
