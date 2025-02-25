from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.setting.settings_resolver import SettingsManager
from gpt_automation.prompt_generator import PromptGenerator
from gpt_automation.setup_settings import SettingContext, PluginArguments


def combine_prompts(dir_prompt, content_prompt):
    combined_prompt = ""
    if dir_prompt:
        combined_prompt += "Directory Structure:\n" + dir_prompt + "\n"
    if content_prompt:
        combined_prompt += "File Contents:\n" + content_prompt.strip()
    return combined_prompt


class PromptManager:
    def __init__(self, root_dir='.', prompt_dir=".", conf_args=None, plugin_file_args=None):
        self.root_dir = root_dir
        self.prompt_dir = prompt_dir
        self.conf_args = conf_args if conf_args is not None else {}
        self.plugin_file_args = plugin_file_args if plugin_file_args is not None else []
        self.settings_manager = SettingsManager(PathManager(root_dir))

    def generate_prompt(self, dir_profiles=None, content_profiles=None, generate_dir=False, generate_content=False):
        if generate_dir:
            dir_prompt = self.generate_directory_prompt(dir_profiles)
        else:
            dir_prompt = ""

        if generate_content:
            content_prompt = self.generate_content_prompt(content_profiles)
        else:
            content_prompt = ""

        if dir_prompt or content_prompt:
            self.display_prompts(dir_prompt, content_prompt)

    def generate_directory_prompt(self, profile_names):
        prompt = self.create_prompt(profile_names, 'directory')
        print("\nDirectory Structure Preview:")
        print(prompt)
        return prompt

    def generate_content_prompt(self, profile_names):
        dir_preview = self.create_prompt(profile_names, 'directory')
        print("\nDirectory Preview for Content (to indicate what has been copied):")
        print(dir_preview)

        content_prompt = self.create_prompt(profile_names, 'content')
        return content_prompt

    def create_prompt(self, profile_names, prompt_type):
        project_info = PromptGenerator(self.prompt_dir,SettingContext(self.root_dir, profile_names),
                                       PluginArguments(self.conf_args, self.plugin_file_args))
        if project_info.initialize():
            if prompt_type == 'directory':
                return project_info.create_directory_structure_prompt()
            elif prompt_type == 'content':
                return project_info.create_file_contents_prompt()
        return "Initialization of directory walker failed."

    def display_prompts(self, dir_prompt, content_prompt):
        combined_prompt = combine_prompts(dir_prompt, content_prompt)
        if combined_prompt:
            self.copy_to_clipboard(combined_prompt)

    def copy_to_clipboard(self, prompt):
        try:
            import pyperclip
            pyperclip.copy(prompt)
            print("\nPrompt has been copied to the clipboard.")
        except ImportError:
            print("\nFailed to copy prompt to clipboard. Pyperclip module not installed.")

# Usage example (this would be outside this code snippet in actual use):
# generator = PromptGenerator()
# generator.generate_prompt(dir_profiles=["profile1"], generate_dir=True)
