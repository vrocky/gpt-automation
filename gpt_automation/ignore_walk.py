import os
import pathlib

from gpt_automation.ignore_file_parser import collect_patterns_from_ignore_files
from gpt_automation.utils.git_tools import find_git_root
from gpt_automation.filters import (
    should_ignore_by_ignore_files,
    filter_with_white_list,
    should_ignore_by_black_list,
    should_include_by_include_only_list,
)
from gpt_automation.utils.pattern_utils import compile_patterns


def traverse_with_filters(path, blacklist, whitelist, profile_name=None,ignore_filenames=['.gitignore', ".gptignore"],
                          include_only_filenames=[".gptincludeonly"]):
    blacklist_patterns = compile_patterns(blacklist)
    whitelist_patterns = compile_patterns(whitelist) if whitelist else None
    include_only_patterns = compile_patterns(include_only_filenames) if include_only_filenames else None

    visited_dirs = set()
    ignore_patterns_stack = initialize_ignore_patterns_stack(path, ignore_filenames)
    include_only_patterns_stack = initialize_ignore_patterns_stack(path, include_only_filenames)

    def walk(directory_path, current_depth):
        if directory_path in visited_dirs:
            return
        visited_dirs.add(directory_path)

        local_ignore_patterns = collect_patterns_from_ignore_files(directory_path, ignore_filenames,profile_name)
        ignore_patterns_stack.append(local_ignore_patterns if local_ignore_patterns else None)

        local_include_only_patterns = collect_patterns_from_ignore_files(directory_path, include_only_filenames,profile_name)
        include_only_patterns_stack.append(local_include_only_patterns if local_include_only_patterns else None)

        subdirectories, file_names = [], []
        for entry in os.scandir(directory_path):
            if entry.is_dir(follow_symlinks=False):
                subdirectories.append(entry.name)
            elif entry.is_file():
                file_names.append(entry.name)

        filtered_filenames = [filename for filename in file_names if
                              not should_ignore_by_ignore_files(os.path.join(directory_path, filename),
                                                                ignore_patterns_stack) and
                              not should_ignore_by_black_list(os.path.join(directory_path, filename),
                                                              blacklist_patterns)]
        filtered_filenames = filter_with_white_list(filtered_filenames, whitelist_patterns)

        filtered_filenames = [filename for filename in filtered_filenames if
                              should_include_by_include_only_list(os.path.join(directory_path, filename),
                                                                  include_only_patterns_stack)]

        yield directory_path, subdirectories, filtered_filenames

        for subdir in subdirectories:
            full_subdir_path = os.path.join(directory_path, subdir)
            if not should_ignore_by_ignore_files(full_subdir_path, ignore_patterns_stack) and \
                    not should_ignore_by_black_list(full_subdir_path, blacklist_patterns):
                yield from walk(full_subdir_path, current_depth + 1)

        ignore_patterns_stack.pop()
        include_only_patterns_stack.pop()

    return walk(path, 0)



def initialize_ignore_patterns_stack(start_path, ignore_filenames):
    git_root_path = find_git_root(start_path)
    patterns_stack = []
    if git_root_path:
        relative_path = os.path.relpath(start_path, git_root_path)
        current_path = git_root_path
        for part in pathlib.Path(relative_path).parts:
            current_path = os.path.join(current_path, part)
            local_pattern_pairs = collect_patterns_from_ignore_files(current_path, ignore_filenames)
            patterns_stack.append(local_pattern_pairs if local_pattern_pairs else None)
    else:
        patterns_stack.append(None)
    return patterns_stack
