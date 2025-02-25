import traceback
from dataclasses import dataclass
from typing import Optional, Dict, List

from gpt_automation.impl.plugin_impl.plugin_init import PluginConfigurationManager
from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.setting.settings_resolver import SettingsResolver


@dataclass
class SettingContext:
    root_dir: str
    profile_names: List[str]


@dataclass
class PluginArguments:
    args: Dict = None
    config_file_args: List = None

    def __post_init__(self):
        self.args = self.args or {}
        self.config_file_args = self.config_file_args or []


class SettingsManager:
    def __init__(self, setting_context: SettingContext):
        self.context = setting_context
        self.path_manager = PathManager(self.context.root_dir)
        self.settings_resolver = SettingsResolver(self.path_manager)
        self.plugin_initializer: Optional[PluginConfigurationManager] = None

    def initialize_settings(self, plugin_arguments: PluginArguments) -> bool:
        """Initialize the system configurations and plugins based on specified profiles"""
        try:
            # Setup base configuration
            self.settings_resolver.create_base_config_if_needed()
            self.settings_resolver.create_profiles(self.context.profile_names)
            self.settings_resolver.copy_gitignore_template()

            # Initialize plugins
            settings = self._load_settings()
            self.plugin_initializer = PluginConfigurationManager(
                self.context.profile_names,
                self.context.root_dir,
                settings=settings
            )
            self._initialize_plugins(plugin_arguments)
            print("System configurations and plugins have been successfully initialized.")
            return True
        except Exception as e:
            print(f"Initialization failed with error: {str(e)}")
            traceback.print_exc()
            return False

    def _load_settings(self):
        """Load and resolve configuration for the specified profiles"""
        try:
            return self.settings_resolver.get_settings(self.context.profile_names)
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            return None

    def _initialize_plugins(self, plugin_arguments: PluginArguments):
        """Initialize and configure plugins"""
        if self.plugin_initializer:
            self.plugin_initializer.setup_and_configure_all_plugins(
                plugin_arguments.args,
                plugin_arguments.config_file_args
            )

    def validate_profiles(self) -> bool:
        """Validate that all profiles are properly initialized and configured"""
        if not self.settings_resolver.check_profiles_created(self.context.profile_names):
            print("Some profiles are missing and need to be created.")
            return False
        print("All profiles are correctly initialized.")
        return True
