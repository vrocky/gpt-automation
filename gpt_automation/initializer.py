from gpt_automation.impl.app_context import AppContext

class Initializer:
    def __init__(self, root_dir, profile_names):
        self.root_dir = root_dir
        self.profile_names = profile_names
        self.app_context = AppContext(root_dir, profile_names)

    def initialize(self):
        """
        Initialize the system configurations and plugins based on specified profiles.
        """
        # Ensure that all profiles are initialized, configuration and plugins are loaded and set up.
        if not self.app_context.initialize_context(self.profile_names):
            print("Initialization of configurations and plugins failed.")
            return False

        # Initialization was successful
        print("System configurations and plugins have been successfully initialized.")
        return True
