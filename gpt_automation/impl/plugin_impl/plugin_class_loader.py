import importlib
from typing import Any, Optional
from gpt_automation.impl.plugin_impl.plugin_utils import LoadResult, LoadStatus

class PluginClassLoader:
    def load_class(self, module_name: str, class_name: str) -> LoadResult:
        """
        Load a plugin class from a module.
        
        Args:
            module_name: Full path to the module
            class_name: Name of the class to load
            
        Returns:
            LoadResult containing the status and loaded class if successful
        """
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            return LoadResult(
                status=LoadStatus.MODULE_NOT_FOUND,
                message=f"Failed to import module {module_name}: {str(e)}"
            )

        try:
            plugin_class = getattr(module, class_name)
        except AttributeError:
            return LoadResult(
                status=LoadStatus.CLASS_NOT_FOUND,
                message=f"Class {class_name} not found in module {module_name}"
            )

        return LoadResult(
            status=LoadStatus.SUCCESS,
            message="Successfully loaded plugin class",
            loaded_item=plugin_class
        )
