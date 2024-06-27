import unittest
from gpt_automation.plugin_impl import PluginManager
from gpt_automation.config.config import Config
import gpt_automation.plugins.ignore_plugin

class TestPluginManager(unittest.TestCase):
    def test_plugin_loading_and_visitors(self):
        # Configuration that mimics what might be loaded from a JSON file
        config_data = {
            "plugins": [
                {
                    "module": "gpt_automation.plugins.ignore_plugin",
                    "class": "IgnorePlugin",
                    "settings": {"ignore_filenames": [".gitignore", ".gptignore"]}
                },
                {
                    "module": "gpt_automation.plugins.include_only_plugin",
                    "class": "IncludeOnlyPlugin",
                    "settings": {
                        "include_only_filenames": [".gptincludeonly"]
                    }
                }
            ]
        }

        config = Config(config_data)

        # Create the PluginManager with this config
        plugin_manager = PluginManager(config)

        # Retrieve all visitors from the plugins
        visitors = plugin_manager.get_all_visitors()

        # Check if the correct number of visitors is returned
        self.assertEqual(len(visitors), 2)  # Assuming each plugin returns one visitor


if __name__ == '__main__':
    unittest.main()
