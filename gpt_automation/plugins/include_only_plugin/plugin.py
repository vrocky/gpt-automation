import os

from gpt_automation.impl.visitor.includeonly_visitor import IncludeOnlyVisitor
from gpt_automation.impl.base_plugin import BasePlugin


class IncludeOnlyPlugin(BasePlugin):

    def is_plugin_configured(self):
        return True

    def configure(self, context):
        pass

    def __init__(self, context, configs, file_args):
        super().__init__(context, configs, file_args)
        self.config_dir = context["plugin_settings_path"]


    def get_visitors(self):
        include_only_visitor = IncludeOnlyVisitor(
            include_only_filenames=self.configs.get('include_only_filenames', []),
            profile_names=self.context.get('profile_names', []))
        return [include_only_visitor]
