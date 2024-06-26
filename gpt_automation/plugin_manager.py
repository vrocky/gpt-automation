class PluginManager:
    def __init__(self):
        self.plugins = []

    def register_plugin(self, plugin):
        self.plugins.append(plugin)

    def get_all_visitors(self):
        visitors = []
        for plugin in self.plugins:
            visitors.extend(plugin.get_visitors())
        return visitors
