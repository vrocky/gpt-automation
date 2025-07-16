# gpt_automation/base_plugin.py
from abc import ABC, abstractmethod

class BasePlugin(ABC):
    def __init__(self):
        """Empty constructor"""
        self.plugin_settings_path = None

    def init(self, plugin_settings_path: str, root_dir: str, profile_names: list):
        """Initialize plugin with required parameters"""
        self.plugin_settings_path = plugin_settings_path
        self.configure(root_dir, profile_names)

    @abstractmethod
    def is_plugin_configured(self):
        """Check if plugin is properly configured"""
        pass

    @abstractmethod
    def get_visitors(self, prompt_dir):
        """Return a list of visitor instances that this plugin wants to use."""
        pass

    @abstractmethod
    def configure(self, root_dir, profile_names):
        """Configure plugin with required parameters"""
        pass

    def activate(self, context):
        """Optional activation hook"""
        pass
