from gpt_automation.impl.config.config_manager import ConfigManager
from gpt_automation.impl.project_info import ProjectInfo


class PromptGenerator:
    def __init__(self, config_manager: ConfigManager, project_path='.'):
        self.project_path = project_path
        self.config_manager = config_manager

    def create_directory_prompt(self, profile_names):
        project_info = ProjectInfo(self.project_path,self.config_manager, profile_names)
        if project_info.initialize():
            return project_info.create_directory_structure_prompt()
        else:
            return ""

    def create_content_prompt(self, profile_names):
        project_info = ProjectInfo(self.project_path,self.config_manager, profile_names)
        if project_info.initialize():
            return project_info.create_file_contents_prompt()
        else:
            return ""

    def generate_prompt(self, dir_profiles=None, content_profiles=None, generate_dir=False, generate_content=False):
        dir_prompt = ""
        content_prompt = ""
        content_prompt_dir_preview = ""

        if generate_dir:
            dir_prompt = self.create_directory_prompt(dir_profiles)

        if generate_content:
            content_prompt_dir_preview = self.create_directory_prompt(content_profiles)
            content_prompt = self.create_content_prompt(content_profiles)

        if dir_prompt:
            print("\nDirectory Structure Preview:")
            print(dir_prompt)

        if content_prompt_dir_preview:
            print("\nDirectory Preview for Content (to indicate what has been copied):")
            print(content_prompt_dir_preview)

        combined_prompt = ""
        if dir_prompt:
            combined_prompt += "Directory Structure:\n" + f"{dir_prompt}\n"
        if content_prompt:
            combined_prompt += "File Contents:\n" + f"{content_prompt}".strip()
        if combined_prompt:
            import pyperclip
            pyperclip.copy(combined_prompt)
            if dir_prompt and content_prompt:
                print("\nBoth directory structure and file contents have been copied to the clipboard.")
            elif dir_prompt:
                print("\nDirectory structure prompt has been copied to the clipboard.")
            elif content_prompt:
                print("\nFile contents prompt has been copied to the clipboard.")
