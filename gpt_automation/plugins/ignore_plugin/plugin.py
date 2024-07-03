import os

from gpt_automation.impl.visitor.ignore_visitor import IgnoreVisitor
from gpt_automation.impl.base_plugin import BasePlugin


class IgnorePlugin(BasePlugin):

    def is_plugin_configured(self):
        return True

    def configure(self, context):
        print("Received init", context)

    def __init__(self, context, configs, settings):
        super().__init__(context, configs, settings)
        self.config_dir = context["plugin_settings_path"]
        self.root_dir = context["root_dir"]
        self.prompt_dir = context["prompt_dir"]

    def get_visitors(self):
        ignore_visitor = IgnoreVisitor(self.root_dir,self.prompt_dir,ignore_filenames=self.configs.get('ignore_filenames', []),
                                       profile_names=self.context.get('profile_names', []))
        return [ignore_visitor]
