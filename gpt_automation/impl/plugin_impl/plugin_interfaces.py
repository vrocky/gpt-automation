from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class IPluginLifecycleCallback(ABC):
    @abstractmethod
    def on_plugin_loaded(self, identifier: str, instance: Any) -> None:
        pass

    @abstractmethod
    def on_plugin_error(self, identifier: str, error: str) -> None:
        pass

class IPluginConfigCallback(ABC):
    @abstractmethod
    def on_config_error(self, identifier: str, error: str) -> None:
        pass

class IConfigurationCallback(ABC):
    @abstractmethod
    def create_plugin_loader(self, context: 'PluginContext') -> 'PluginLoader':
        pass

    @abstractmethod
    def on_config_loaded(self, identifier: str, context: 'PluginContext') -> 'PluginContext':
        pass

    @abstractmethod
    def on_config_error(self, identifier: str, error: str) -> None:
        pass
