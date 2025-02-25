from gpt_automation.plugins.ignore_plugin.ignore_visitor import IgnoreVisitor
from gpt_automation.impl.base_plugin import BasePlugin

class IgnorePlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.config_dir = None
        self.root_dir = None
        self.settings_args = None
        self.profile_names = None

    def configure(self, context):
        self.config_dir = self.plugin_settings_path
        self.root_dir = context.get('root_dir', '')
        self.settings_args = context.get('settings_args', {})
        self.profile_names = context.get('profile_names', [])

    def is_plugin_configured(self):
        return True

    def get_visitors(self, prompt_dir):
        ignore_visitor = IgnoreVisitor(
            self.root_dir, 
            prompt_dir,
            ignore_filenames=self.settings_args.get('ignore_filenames', []),
            profile_names=self.profile_names
        )
        return [ignore_visitor]
