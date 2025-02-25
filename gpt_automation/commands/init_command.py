from gpt_automation.setup_settings import SettingContext, PluginArguments, SettingsSetup

class InitCommand:
    def __init__(self, root_dir: str, profile_names: list[str]):
        self.root_dir = root_dir
        self.profile_names = profile_names

    def execute(self):
        print(f"Root Directory: {self.root_dir}")
        setup_context = SettingContext(root_dir=self.root_dir, profile_names=self.profile_names)
        plugin_arguments = PluginArguments(args={}, config_file_args=[])  # Default empty arguments
        config_creator = SettingsSetup(setup_context, plugin_arguments)
        config_creator.create_settings()
