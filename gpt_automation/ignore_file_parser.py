import os

def parse_gptignore_file(ignore_file_path, profile_name=None):
    """
    Parses a .gptignore file, returning patterns applicable globally and for the specified profile.

    :param ignore_file_path: Path to the .gptignore file.
    :param profile_name: Name of the profile to filter for specific patterns.
    :return: A tuple containing two lists - global patterns and profile-specific patterns.
    """
    global_patterns = []
    profiles_patterns = {}
    current_profile = None

    with open(ignore_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            # Detect profile section headers
            if line.startswith('[') and line.endswith(']'):
                current_profile = line[1:-1]
                if current_profile not in profiles_patterns:
                    profiles_patterns[current_profile] = []
            elif current_profile:
                # Collect patterns for the current profile section
                profiles_patterns[current_profile].append(line)
            else:
                # Collect global patterns
                global_patterns.append(line)

    # If a profile is specified, return its specific patterns along with global patterns
    if profile_name:
        profile_specific_patterns = profiles_patterns.get(profile_name, [])
        return global_patterns, profile_specific_patterns
    # If no profile is specified, return only the global patterns
    else:
        return global_patterns, []

def collect_patterns_from_ignore_files(directory_path, ignore_filenames, profile_name=None):
    """
    Collects patterns from .gptignore or similar files, considering global and profile-specific patterns.

    :param directory_path: Directory path to search for ignore files.
    :param ignore_filenames: List of ignore filenames, like ['.gptignore'].
    :param profile_name: Optional profile name to filter profile-specific patterns.
    :return: A list of (base_path, pattern) pairs for the ignore mechanism.
    """
    pattern_pairs = []
    if ignore_filenames:
        for ignore_filename in ignore_filenames:
            ignore_file_path = os.path.join(directory_path, ignore_filename)
            if os.path.isfile(ignore_file_path):
                global_patterns, profile_specific_patterns = parse_gptignore_file(ignore_file_path, profile_name)
                patterns = global_patterns + profile_specific_patterns
                pattern_pairs.extend([(directory_path, pattern) for pattern in patterns])
    return pattern_pairs
