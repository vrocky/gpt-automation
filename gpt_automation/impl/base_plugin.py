# gpt_automation/base_plugin.py
from abc import ABC, abstractmethod

class BasePlugin(ABC):
    def __init__(self):
        """Empty constructor"""
        self.context = None
        self.plugin_settings_path = None

    def init(self, context):
        """Initialize plugin with context"""
        self.context = context
        self.plugin_settings_path = context['plugin_settings_path']
        self.configure(context)

    @abstractmethod
    def is_plugin_configured(self):
        """Check if plugin is properly configured"""
        pass

    @abstractmethod
    def get_visitors(self, prompt_dir):
        """Return a list of visitor instances that this plugin wants to use."""
        pass

    @abstractmethod
    def configure(self, context):
        """Configure plugin with context"""
        pass

    def activate(self, context):
        """Optional activation hook"""
        pass
