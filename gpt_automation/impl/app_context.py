from gpt_automation.impl.app import App


class AppContext:
    def __init__(self, root_dir, profile_names):
        self.app = App(root_dir, profile_names)

    def get_path_manager(self):
        return self.app.path_manager

    def get_config_manager(self):
        return self.app.config_manager

    def get_plugin_manager(self):
        return self.app.plugin_manager

    def get_root_dir(self):
        return self.app.root_dir

    def check_profile_created(self):
        return self.app.check_profiles_created()

    def create_profiles(self):
        return self.app.create_profiles()

    def load_plugins(self):
        return self.app.load_plugins()
