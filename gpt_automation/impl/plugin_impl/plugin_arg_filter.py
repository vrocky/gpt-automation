class PluginArgFilter:
    def __init__(self, raw_args):
        if not isinstance(raw_args, dict):
            raise ValueError("Expected raw_args to be a dictionary.")
        self.plugin_args = self._preprocess_args(raw_args)

    def _preprocess_args(self, raw_args):
        """
        Preprocesses the raw arguments into a structured dictionary.
        """
        processed_args = {}
        for key, value in raw_args.items():
            parts = key.split('__')
            if len(parts) >= 3:
                package_plugin = '__'.join(parts[:2])
                variable_name = '__'.join(parts[2:])
                if package_plugin not in processed_args:
                    processed_args[package_plugin] = {}
                processed_args[package_plugin][variable_name] = value
            else:
                print(f"Warning: Argument key '{key}' is not properly formatted.")
        return processed_args

    def get_plugin_args(self, package_name, plugin_name):
        """
        Retrieves preprocessed arguments for a specific plugin. Returns default values if no arguments are found.
        """
        key = f"{package_name}__{plugin_name}"
        # Provide a default dictionary in case no arguments are found
        return self.plugin_args.get(key, {})

if __name__ == '__main__':
    args = {
        "mypackage__pluginA__timeout": 30,
        "mypackage__pluginA__debug": True,
        "mypackage__pluginB__debug": True,
        "otherpackage__pluginC__feature": "enabled"
    }

    arg_filter = PluginArgFilter(args)
    pluginA_args = arg_filter.get_plugin_args("mypackage", "pluginA")
    pluginB_args = arg_filter.get_plugin_args("mypackage", "pluginB")
    pluginC_args = arg_filter.get_plugin_args("otherpackage", "pluginC")

    print(f"Arguments for Plugin A: {pluginA_args}")
    print(f"Arguments for Plugin B: {pluginB_args}")
    print(f"Arguments for Plugin C: {pluginC_args}")
