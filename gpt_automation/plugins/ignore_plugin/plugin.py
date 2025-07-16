from gpt_automation.plugins.ignore_plugin.ignore_visitor import IgnoreVisitor
from gpt_automation.impl.base_plugin import BasePlugin

class IgnorePlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.config_dir = None
        self.root_dir = None
        self.settings_args = None
        self.profile_names = None

    def init(self, plugin_settings_path: str, root_dir: str, profile_names: list):
        """Initialize plugin with all required parameters"""
        self.plugin_settings_path = plugin_settings_path
        self.config_dir = plugin_settings_path
        self.configure(root_dir, profile_names)

    def configure(self, root_dir, profile_names):
        """Configure plugin with required parameters"""
        self.root_dir = root_dir
        self.profile_names = profile_names

    def is_plugin_configured(self):
        return True

    def get_visitors(self, prompt_dir):
        ignore_visitor = IgnoreVisitor(
            self.root_dir, 
            prompt_dir,
            ignore_filenames=self.settings_args.get('ignore_filenames', []) if self.settings_args else [],
            profile_names=self.profile_names
        )
        return [ignore_visitor]
