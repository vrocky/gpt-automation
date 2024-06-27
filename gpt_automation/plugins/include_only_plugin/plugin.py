import os

from gpt_automation.visitor.includeonly_visitor import IncludeOnlyVisitor
from gpt_automation.base_plugin import BasePlugin


class IncludeOnlyPlugin(BasePlugin):

    def __init__(self, context, settings):
        BasePlugin.__init__(self, context, settings)
        self.config_dir = context["plugin_settings_path"]

    def get_visitors(self):
        include_only_visitor = IncludeOnlyVisitor(
            include_only_filenames=self.settings.get('include_only_filenames', []),
            profile_names=self.context.get('profile_names', []))
        return [include_only_visitor]
