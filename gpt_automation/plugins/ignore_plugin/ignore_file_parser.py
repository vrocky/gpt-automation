import os


def parse_gptignore_file(ignore_file_path, profile_names=None):
    """
    Parses a .gptignore file, storing and returning patterns applicable globally and for specified profiles,
    with proper handling for grouped headers sharing patterns.

    :param ignore_file_path: Path to the .gptignore file.
    :param profile_names: List of profile names to specifically filter patterns for.
    :return: A dictionary containing global patterns and profile-specific patterns for each requested profile.
    """
    global_patterns = []
    profile_map = {}
    current_profiles = []

    with open(ignore_file_path, 'r') as file:
        lines = file.readlines()

    # Remove leading and trailing whitespaces and filter out empty lines and comments
    lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('[') and line.endswith(']'):
            # New header found, start collecting new set of headers
            current_profiles = [line[1:-1]]
            i += 1
            # Collect all consecutive headers
            while i < len(lines) and lines[i].startswith('[') and lines[i].endswith(']'):
                current_profiles.append(lines[i][1:-1])
                i += 1

            # Collect patterns for all these headers
            while i < len(lines) and not lines[i].startswith('['):
                for profile in current_profiles:
                    if profile in profile_map:
                        profile_map[profile].append(lines[i])
                    else:
                        profile_map[profile] = [lines[i]]
                i += 1
        else:
            # Global patterns
            global_patterns.append(line)
            i += 1

    # Prepare output dictionary, merging global and profile-specific patterns
    output_patterns = {'global': global_patterns}
    for profile in profile_names or []:
        output_patterns[profile] = global_patterns + profile_map.get(profile, [])

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

