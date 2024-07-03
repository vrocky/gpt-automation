from gpt_automation.impl.app_context import AppContext
from gpt_automation.project_info import ProjectInfo


def combine_prompts(dir_prompt, content_prompt):
    combined_prompt = ""
    if dir_prompt:
        combined_prompt += "Directory Structure:\n" + dir_prompt + "\n"
    if content_prompt:
        combined_prompt += "File Contents:\n" + content_prompt.strip()
    return combined_prompt


class PromptGenerator:
    def __init__(self, root_dir='.', prompt_dir= ".", conf_args=None, plugin_file_args=None):
        if conf_args is None:
            conf_args = {}
        if plugin_file_args is None:
            plugin_file_args = []

        self.root_dir = root_dir
        self.prompt_dir = prompt_dir
        self.conf_args = conf_args
        self.plugin_file_args = plugin_file_args

    def generate_prompt(self, dir_profiles=None, content_profiles=None, generate_dir=False, generate_content=False):
        dir_prompt = ""
        content_prompt = ""
        content_prompt_dir_preview = ""

        # Generate directory structure prompt if requested
        if generate_dir:
            dir_prompt = self.create_directory_prompt(dir_profiles)

        # Generate content prompt if requested
        if generate_content:
            # Get directory structure preview for the content profiles
            content_prompt_dir_preview = self.create_directory_prompt(content_profiles)
            # Get content based on the content profiles
            content_prompt = self.create_content_prompt(content_profiles)

        # Output the directory structure prompt
        if dir_prompt:
            print("\nDirectory Structure Preview:")
            print(dir_prompt)

        # Output the directory preview specifically for content generation
        if content_prompt_dir_preview:
            print("\nDirectory Preview for Content (to indicate what has been copied):")
            print(content_prompt_dir_preview)

        # Combine and copy prompts to the clipboard
        combined_prompt = combine_prompts(dir_prompt, content_prompt)
        if combined_prompt:
            self.copy_to_clipboard(combined_prompt)

    def create_directory_prompt(self, profile_names):
        return self.create_prompt(profile_names, prompt_type='directory')

    def create_content_prompt(self, profile_names):
        return self.create_prompt(profile_names, prompt_type='content')

    def create_prompt(self, profile_names, prompt_type):
        app_context = AppContext(self.root_dir,self.prompt_dir, profile_names, self.conf_args, self.plugin_file_args)
        project_info = ProjectInfo(app_context)
        if project_info.are_profiles_initialized():
            if project_info.initialize():
                if prompt_type == 'directory':
                    return project_info.create_directory_structure_prompt()
                elif prompt_type == 'content':
                    return project_info.create_file_contents_prompt()
            else:
                return "Initialization of directory walker failed."
        else:
            return "Profiles are not initialized. Please run the 'init' command."

    def copy_to_clipboard(self, prompt):
        import pyperclip
        pyperclip.copy(prompt)
        print("\nPrompt has been copied to the clipboard.")
