from gpt_automation.impl.plugin_impl.plugin_init import PluginConfigurationManager
from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.setting.settings_manager import SettingsManager


class InitConfig:
    def __init__(self, setup_context):
        self.context = setup_context
        self.path_manager = PathManager(self.context.root_dir)
        self.settings_manager = SettingsManager(self.path_manager)

    def setup_initial_config(self, plugin_args):
        """
        Setup the initial configuration for the application including directories, profiles,
        and plugins based on provided specifications.
        """
        self.settings_manager.create_base_config_if_needed()
        self.settings_manager.create_profiles(self.context.profile_names)
        self.plugin_initializer = PluginConfigurationManager(
            self.context.profile_names,
            self.context.root_dir,
            settings=self.load_settings()
        )
        self.initialize_and_configure_plugins(plugin_args.args, plugin_args.config_file_args)
        print("Initial configuration setup is complete.")

    def load_settings(self):
        """ Load and resolve configuration for the specified profiles. """
        try:
            return self.settings_manager.get_settings(self.context.profile_names)
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            return None

    def initialize_and_configure_plugins(self, plugin_args, config_file_args):
        """ Initialize and configure plugins using PluginConfigInitializer. """
        self.plugin_initializer.setup_and_configure_all_plugins(plugin_args, config_file_args)

    def validate_profiles(self):
        """ Validate that all profiles are properly initialized and configured. """
        if not self.settings_manager.check_profiles_created(self.context.profile_names):
            print("Some profiles are missing and need to be created.")
            return False
        print("All profiles are correctly initialized.")
        return True
