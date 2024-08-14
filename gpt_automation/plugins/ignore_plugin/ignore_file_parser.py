import os


def parse_gptignore_file(ignore_file_path, profile_names=None):
    global_patterns = []
    profiles_patterns = {}
    active_profiles = []

    with open(ignore_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('[') and line.endswith(']'):
                # Starting a new profile block, flush previous active profiles
                if line != active_profiles[-1] if active_profiles else None:
                    active_profiles = []
                current_profile = line[1:-1]
                active_profiles.append(current_profile)
                if current_profile not in profiles_patterns:
                    profiles_patterns[current_profile] = []
            elif active_profiles:
                for profile in active_profiles:
                    profiles_patterns[profile].append(line)
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
