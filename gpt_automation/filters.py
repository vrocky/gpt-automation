from gpt_automation.Ignore_match import IgnoreMatch
from gpt_automation.utils.pattern_utils import matches_list_pattern


def load_ignore_matches(base_pattern_pairs):
    if base_pattern_pairs:
        return IgnoreMatch(base_pattern_pairs)
    else:
        return None


def should_ignore_by_ignore_files(file_path, ignore_matches_stack):
    for base_pattern_pairs in reversed(ignore_matches_stack):
        if base_pattern_pairs:
            ignore_match = load_ignore_matches(base_pattern_pairs)
            if ignore_match and ignore_match.match(file_path):
                return True
    return False


def should_ignore_by_black_list(file_path, black_list_patterns):
    return matches_list_pattern(file_path, black_list_patterns)


def load_ignore_matches(base_pattern_pairs):
    if base_pattern_pairs:
        return IgnoreMatch(base_pattern_pairs)
    else:
        return None

def should_include_by_include_only_list(file_path, include_only_matches_stack):
    # Normalize file path to be consistent with pattern matching logic
    file_path = file_path.replace("\\", "/").lstrip("/")

    print("Normalized file path:", file_path)  # Debugging output

    # Pre-load IgnoreMatch objects from the stack to avoid repeated loading
    preloaded_include_matches = [
        load_ignore_matches(include_only_paths) for include_only_paths in include_only_matches_stack if include_only_paths
    ]

    # Print loaded matches for debugging
    print("Loaded Include Matches:", preloaded_include_matches)

    # Determine if any IgnoreMatch object has matches
    active_include_only_rules = any(match.has_matches() for match in preloaded_include_matches if match)
    print("Active include-only rules exist:", active_include_only_rules)  # Debugging output

    # If no active rules are found, the feature is not in use, so return True
    if not active_include_only_rules:
        return True

    # Check matches with preloaded IgnoreMatch objects
    for include_match in reversed(preloaded_include_matches):
        print("Checking match for file:", file_path, "with", include_match)  # Debugging output before if-else part
        if include_match and include_match.match(file_path):
            print(f"File {file_path} matches include-only pattern: {include_match}")  # Debugging output
            return True
        else:
            print(f"File {file_path} does not match pattern: {include_match}")  # Debugging output for else part

    print(f"File {file_path} does not match any include-only patterns")  # Debugging output
    # If the file does not match any include-only patterns, it should not be included
    return False




def filter_with_white_list(filtered_filenames, white_list_patterns):
    if white_list_patterns and len(white_list_patterns) > 0:
        return [filename for filename in filtered_filenames if matches_list_pattern(filename, white_list_patterns)]
    else:
        return filtered_filenames
