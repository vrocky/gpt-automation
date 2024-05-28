# gpt_automation\project_info.py
import os
import gpt_automation.ignore_walk


class ProjectInfo:
    def __init__(self, root_dir, black_list=None, white_list=None, profile_names=None):
        self.root_dir = root_dir
        self.black_list = black_list.strip().split('\n') if black_list else []
        self.white_list = white_list.strip().split('\n') if white_list else []
        self.profile_names = profile_names

    def create_directory_structure_prompt(self):
        prompt = "Directory Structure:\n"
        for root, dirs, files in gpt_automation.ignore_walk.traverse_with_filters(self.root_dir, self.black_list,
                                                                                  self.white_list, self.profile_names):
            level = root.replace(self.root_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            prompt += '{}{}/\n'.format(indent, os.path.basename(root))
            sub_indent = ' ' * 4 * (level + 1)
            for file in files:
                prompt += '{}{}\n'.format(sub_indent, os.path.basename(file))
        return prompt

    def create_file_contents_prompt(self):
        prompt = "File Contents:\n"
        for root, dirs, files in gpt_automation.ignore_walk.traverse_with_filters(self.root_dir, self.black_list,
                                                                                  self.white_list, self.profile_names):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.root_dir)
                with open(file_path, 'r', encoding='utf-8') as f:
                    prompt += '{}{}:\n'.format('=' * 10, relative_path)
                    prompt += f.read() + '\n\n'
        return prompt
