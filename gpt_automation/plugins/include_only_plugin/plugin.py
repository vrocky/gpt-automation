from gpt_automation.plugins.include_only_plugin.includeonly_visitor import IncludeOnlyVisitor
from gpt_automation.impl.base_plugin import BasePlugin

class IncludeOnlyPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.root_dir = None
        self.settings_args = None
        self.profile_names = None

    def init(self, plugin_settings_path: str, root_dir: str, profile_names: list):
        """Initialize plugin with all required parameters"""
        self.plugin_settings_path = plugin_settings_path
        self.configure(root_dir, profile_names)

    def configure(self, root_dir, profile_names):
        """Configure plugin with required parameters"""
        self.root_dir = root_dir
        self.profile_names = profile_names

    def is_plugin_configured(self):
        return self.plugin_settings_path is not None and self.root_dir is not None

    def get_visitors(self, prompt_dir):
        include_only_visitor = IncludeOnlyVisitor(
            self.root_dir,
            prompt_dir,
            include_only_filenames=self.settings_args.get('include_only_filenames', []) if self.settings_args else [],
            profile_names=self.profile_names
        )
        return [include_only_visitor]
