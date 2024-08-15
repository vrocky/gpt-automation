import traceback

from gpt_automation.setup_config import SetupConfig


class SetupContext:
    def __init__(self, root_dir, profile_names):
        self.root_dir = root_dir
        self.profile_names = profile_names

    def __str__(self):
        return f"SetupContext(root_dir={self.root_dir}, profile_names={self.profile_names})"


class PluginArguments:
    def __init__(self, args=None, config_file_args=None):
        if args is None:
            args = {}
        if config_file_args is None:
            config_file_args = []

        self.args = args
        self.config_file_args = config_file_args

    def __str__(self):
        return f"PluginArguments(args={self.args}, file_args={self.config_file_args})"


class SettingsSetup:
    def __init__(self, setup_context, plugin_arguments):
        self.context = setup_context
        self.arguments = plugin_arguments
        self.init_config = SetupConfig(setup_context)

    def create_settings(self):
        """
        Initialize the system configurations and plugins based on specified profiles
        using the InitConfig class.
        """
        try:
            self.init_config.setup_initial_config(self.arguments)
            print("System configurations and plugins have been successfully initialized.")
            return True
        except Exception as e:
            print(f"Initialization failed with an error: {str(e)}")
            traceback.print_exc()
            return False
