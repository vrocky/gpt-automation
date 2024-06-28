import os


def parse_gptignore_file(ignore_file_path, profile_names=None):
    """
    Parses a .gptignore file, returning patterns applicable globally and for the specified profiles.

    :param ignore_file_path: Path to the .gptignore file.
    :param profile_names: List of names of the profiles to filter for specific patterns.
    :return: A dictionary containing global patterns and profile-specific patterns for each requested profile.
    """
    global_patterns = []
    profiles_patterns = {}
    current_profile = None

    with open(ignore_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('[') and line.endswith(']'):
                current_profile = line[1:-1]
                profiles_patterns[current_profile] = []
            elif current_profile:
                profiles_patterns[current_profile].append(line)
            else:
                global_patterns.append(line)

    # Prepare the output dictionary
    output_patterns = {'global': global_patterns}
    for profile in profile_names or []:
        output_patterns[profile] = global_patterns + profiles_patterns.get(profile, [])
    return output_patterns


def generate_pattern_pairs(directory_path, patterns):
    """
    Generates (base_path, pattern) pairs for the given directory path and patterns.

    :param directory_path: Base directory path.
    :param patterns: List of patterns.
    :return: A list of (base_path, pattern) pairs.
    """
    return [(directory_path, pattern) for pattern in patterns]


def collect_patterns_from_ignore_files(directory_path, ignore_filenames, profile_names=None):
    """
    Collects and combines patterns from .gptignore or similar files, considering global and profile-specific patterns.

    :param directory_path: Directory path to search for ignore files.
    :param ignore_filenames: List of ignore filenames, like ['.gptignore'].
    :param profile_names: Optional list of profile names to filter profile-specific patterns.
    :return: A list of (base_path, pattern) pairs for the ignore mechanism.
    """
    pattern_pairs = []
    if ignore_filenames:
        for ignore_filename in ignore_filenames:
            ignore_file_path = os.path.join(directory_path, ignore_filename)
            if os.path.isfile(ignore_file_path):
                profiles_patterns = parse_gptignore_file(ignore_file_path, profile_names)
                for patterns in profiles_patterns.values():
                    pattern_pairs.extend(generate_pattern_pairs(directory_path, patterns))
    return pattern_pairs
