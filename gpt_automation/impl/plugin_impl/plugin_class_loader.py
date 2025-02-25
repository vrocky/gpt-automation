import importlib
from typing import Optional, Type
from gpt_automation.impl.plugin_impl.plugin_utils import LoadStatus, LoadResult
from gpt_automation.impl.base_plugin import BasePlugin

class PluginClassLoader:
    def load_class(self, module_name: str, class_name: str) -> LoadResult:
        """
        Load a plugin class from a module
        
        Args:
            module_name: Name of the module to load from
            class_name: Name of the class to load
            
        Returns:
            LoadResult containing status and loaded class if successful
        """
        try:
            # Import the module
            module = importlib.import_module(module_name)
            if not module:
                return LoadResult(
                    LoadStatus.MODULE_NOT_FOUND,
                    f"Module {module_name} not found"
                )

            # Get the class from the module
            plugin_class = getattr(module, class_name, None)
            if not plugin_class:
                return LoadResult(
                    LoadStatus.CLASS_NOT_FOUND,
                    f"Class {class_name} not found in module {module_name}"
                )

            # Verify the class is a proper plugin class
            if not issubclass(plugin_class, BasePlugin):
                return LoadResult(
                    LoadStatus.INVALID_CLASS,
                    f"Class {class_name} in {module_name} is not a BasePlugin subclass"
                )

            return LoadResult(
                LoadStatus.SUCCESS,
                "Successfully loaded plugin class",
                plugin_class
            )

        except ImportError as e:
            return LoadResult(
                LoadStatus.MODULE_NOT_FOUND,
                f"Failed to import module {module_name}: {str(e)}"
            )
        except Exception as e:
            return LoadResult(
                LoadStatus.INITIALIZATION_ERROR,
                f"Error loading plugin class: {str(e)}"
            )
