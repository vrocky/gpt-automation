import traceback

from gpt_automation.init_config import InitConfig


class SettingsSetup:
    def __init__(self, root_dir, profile_names, config_args=None, plugin_file_args=None):
        if plugin_file_args is None:
            plugin_file_args = []
        if config_args is None:
            config_args = {}

        self.root_dir = root_dir
        self.profile_names = profile_names
        self.config_args = config_args
        self.plugin_file_args = plugin_file_args
        self.init_config = InitConfig(self.root_dir, self.profile_names, self.config_args, self.plugin_file_args)

    def create_settings(self):
        """
        Initialize the system configurations and plugins based on specified profiles
        using the InitConfig class.
        """
        # Directly call the setup_initial_config method from InitConfig
        try:
            self.init_config.setup_initial_config(self.config_args, self.plugin_file_args)
            print("System configurations and plugins have been successfully initialized.")
            return True
        except Exception as e:
            # Print the error message
            print(f"Initialization failed with an error: {str(e)}")
            # Print the stack trace
            print("Stack trace:")
            traceback.print_exc()
            return False

