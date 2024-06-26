from gpt_automation.visitor.ignore_visitor import IgnoreVisitor
from gpt_automation.plugins.base_plugin import BasePlugin


class IgnorePlugin(BasePlugin):
    def get_visitors(self):
        ignore_visitor = IgnoreVisitor(ignore_filenames=self.settings.get('ignore_filenames', []),
                                       profile_names=self.env.get('profile_names', []))
        return [ignore_visitor]
