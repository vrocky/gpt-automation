# gpt_automation/base_plugin.py
from abc import ABC, abstractmethod


class BasePlugin(ABC):
    def __init__(self, context, settings):
        self.context = context
        self.settings = settings

    @abstractmethod
    def get_visitors(self):
        """
        Return a list of visitor instances that this plugin wants to use.
        """
        pass

    @abstractmethod
    def initialize(self, context):
        """
        Initialize necessary resources or perform setup tasks with provided context.
        """
        pass
