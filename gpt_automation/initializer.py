from gpt_automation.config.config_manager import ConfigManager
from gpt_automation.plugin_impl.manager.plugin_runtime_manager import PluginRuntimeManager


class Initializer:
    def __init__(self, profile_names):
        self.profile_names = profile_names
        self.config_manager = ConfigManager()
        self.plugin_manager = PluginRuntimeManager(self.profile_names, self.config_manager)

    def initialize(self):
        if not self.profile_names:
            self.config_manager.initialize_configurations()  # Initialize default configurations
        else:
            for profile in set(self.profile_names):  # Use a set to avoid initializing the same profile more than once
                self.config_manager.initialize_profile_config(profile)

        # Load and initialize plugins after setting up configurations
        self.plugin_manager.load_plugin_classes()
        self.plugin_manager.create_plugin_instances()
        self.plugin_manager.initialize_plugins()

