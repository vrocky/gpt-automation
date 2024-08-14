from gpt_automation.plugins.include_only_plugin.includeonly_visitor import IncludeOnlyVisitor
from gpt_automation.impl.base_plugin import BasePlugin


class IncludeOnlyPlugin(BasePlugin):

    def is_plugin_configured(self):
        return True

    def configure(self, context):
        pass

    def __init__(self, context, configs, file_args):
        super().__init__(context, configs, file_args)
        self.config_dir = context["plugin_settings_path"]
        self.root_dir = context["root_dir"]
        self.prompt_dir = context["prompt_dir"]


    def get_visitors(self):
        include_only_visitor = IncludeOnlyVisitor(self.root_dir,self.prompt_dir,
            include_only_filenames=self.configs.get('include_only_filenames', []),
            profile_names=self.context.get('profile_names', []))
        return [include_only_visitor]
