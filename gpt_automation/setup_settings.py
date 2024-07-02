from gpt_automation.impl.app_context import AppContext


class SettingsSetup:
    def __init__(self, root_dir, profile_names, config_args=None, plugin_file_args=None):
        if plugin_file_args is None:
            plugin_file_args = []
        if config_args is None:
            config_args = []
        self.root_dir = root_dir
        self.profile_names = profile_names
        self.app_context = AppContext(root_dir,
                                      profile_names,
                                      conf_args=config_args,
                                      plugin_file_args=plugin_file_args)

    def create_settings(self):
        """
        Initialize the system configurations and plugins based on specified profiles.
        """
        # Ensure that all profiles are initialized, configuration and plugins are loaded and set up.
        if not self.app_context.create_profiles():
            print("Initialization of configurations and plugins failed.")
            return False

        # Initialization was successful
        print("System configurations and plugins have been successfully initialized.")
        return True
