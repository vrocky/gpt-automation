import importlib


class PluginManager:
    def __init__(self,env = None,config=None):
        self.plugins = []
        if config is not None:
            self.load_plugins(env,config)

    def register_plugin(self, plugin):
        self.plugins.append(plugin)

    def get_all_visitors(self):
        visitors = []
        for plugin in self.plugins:
            visitors.extend(plugin.get_visitors())
        return visitors

    def load_plugins(self, env,config):
        plugins_config = config.data.get('plugins', [])
        for plugin_info in plugins_config:
            module_path = plugin_info['module']
            class_name = plugin_info['class']
            settings = plugin_info['settings']
            module = importlib.import_module(module_path)
            plugin_class = getattr(module, class_name)
            plugin_instance = plugin_class(env,settings)
            self.register_plugin(plugin_instance)
