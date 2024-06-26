from gpt_automation.visitor.includeonly_visitor import IncludeOnlyVisitor
from gpt_automation.plugins.base_plugin import BasePlugin


class IncludeOnlyPlugin(BasePlugin):
    def get_visitors(self):
        include_only_visitor = IncludeOnlyVisitor(
            include_only_filenames=self.settings.get('include_only_filenames', []),
            profile_names=self.settings.get('profile_names', []))
        return [include_only_visitor]
