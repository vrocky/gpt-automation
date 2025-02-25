import os
import sys
from gpt_automation.prompt_manager import PromptManager

class PromptCommand:
    def __init__(self, root_dir: str, prompt_dir: str, profiles: list[str], 
                 dir_profiles: list[str], content_profiles: list[str],
                 generate_dir: bool = True, generate_content: bool = True):
        self.root_dir = root_dir
        self.prompt_dir = prompt_dir
        self.profiles = profiles
        self.dir_profiles = dir_profiles
        self.content_profiles = content_profiles
        self.generate_dir = generate_dir
        self.generate_content = generate_content

    def execute(self):
        print(f"Root Directory: {self.root_dir}")
        print(f"Prompt Directory: {self.prompt_dir}")

        if not self._validate_directories():
            print(f"Error: 'prompt_dir' {self.prompt_dir} must be a subdirectory of 'root_dir' {self.root_dir} or the same.")
            sys.exit(1)

        prompt_generator = PromptManager(
            root_dir=self.root_dir, 
            prompt_dir=self.prompt_dir
        )

        prompt_generator.generate_prompt(
            dir_profiles=self.dir_profiles,
            content_profiles=self.content_profiles,
            generate_dir=self.generate_dir,
            generate_content=self.generate_content
        )

    def _validate_directories(self) -> bool:
        relative_path = os.path.relpath(self.prompt_dir, self.root_dir)
        return relative_path == '.' or not relative_path.startswith('..')
