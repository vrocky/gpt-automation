from gpt_automation.plugins.include_only_plugin.includeonly_visitor import IncludeOnlyVisitor
from gpt_automation.impl.base_plugin import BasePlugin

class IncludeOnlyPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.config_dir = None
        self.root_dir = None
        self.settings_args = None
        self.profile_names = None

    def configure(self, root_dir, profile_names):
        self.config_dir = self.plugin_settings_path
        self.root_dir = root_dir
        self.profile_names = profile_names

    def is_plugin_configured(self):
        return True

    def get_visitors(self, prompt_dir):
        include_only_visitor = IncludeOnlyVisitor(
            self.root_dir,
            prompt_dir,
            include_only_filenames=self.settings_args.get('include_only_filenames', []) if self.settings_args else [],
            profile_names=self.profile_names
        )
        return [include_only_visitor]
