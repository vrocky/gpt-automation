import os

from gpt_automation.impl.visitor.ignore_visitor import IgnoreVisitor
from gpt_automation.impl.base_plugin import BasePlugin


class IgnorePlugin(BasePlugin):

    def is_plugin_configured(self):
        return True

    def configure(self, context):
        print("Received init", context)

    def __init__(self, context, config_args, file_args, settings):
        super().__init__(context, config_args, file_args, settings)
        self.config_dir = context["plugin_settings_path"]

    def get_visitors(self):
        ignore_visitor = IgnoreVisitor(ignore_filenames=self.settings.get('ignore_filenames', []),
                                       profile_names=self.context.get('profile_names', []))
        return [ignore_visitor]
