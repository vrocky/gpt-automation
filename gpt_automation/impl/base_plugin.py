# gpt_automation/base_plugin.py
from abc import ABC, abstractmethod


class BasePlugin(ABC):
    def __init__(self, context, args, file_args, settings):
        self.context = context
        self.settings = settings
        self.args = args
        self.file_args = file_args

    @abstractmethod
    def is_plugin_configured(self):
        pass

    @abstractmethod
    def get_visitors(self, profile_names):
        """
        Return a list of visitor instances that this plugin wants to use.
        """
        pass

    @abstractmethod
    def configure(self, profile_names):
        """
        Initialize necessary resources or perform setup tasks with provided context.
        """
        pass
