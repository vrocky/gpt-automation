"""Discover project root by searching for .gpt/ directory."""

import os
from pathlib import Path


class RootLookup:
    """Find the project root by recursively searching for the .gpt/ marker directory."""

    def __init__(self, initial_dir, provided_root_dir=None):
        """
        Initialize RootLookup.

        Args:
            initial_dir: Starting directory for search
            provided_root_dir: Explicit root directory (takes precedence over search)
        """
        self.initial_dir = initial_dir
        self.provided_root_dir = provided_root_dir

    def find_root_directory(self):
        """
        Recursively checks parent directories from initial_dir to find the '.gpt' directory.

        Returns the directory containing the '.gpt' directory as the root, if found.
        Returns None if not found.
        """
        current_dir = self.initial_dir
        try:
            while current_dir != os.path.dirname(current_dir):  # Stop at filesystem root
                if os.path.exists(current_dir) and '.gpt' in os.listdir(current_dir):
                    return current_dir
                current_dir = os.path.dirname(current_dir)
        except (FileNotFoundError, OSError):
            pass
        return None

    def determine_directories(self, prompt_dir=None):
        """
        Determine the root and prompt directories based on provided arguments.

        Args:
            prompt_dir: Optional specific directory to analyze

        Returns:
            Tuple of (root_dir, prompt_dir) as strings

        Raises:
            ValueError: If directories are invalid or not found
        """
        root_dir = self.provided_root_dir or self.find_root_directory()
        if not root_dir or not os.path.exists(root_dir):
            raise ValueError(f"Could not find valid root directory. Provided or discovered path: {root_dir}")

        final_prompt_dir = prompt_dir or self.initial_dir
        if not os.path.exists(final_prompt_dir):
            raise ValueError(f"Prompt directory does not exist: {final_prompt_dir}")

        # Validate prompt directory is within root
        try:
            relative_path = os.path.relpath(final_prompt_dir, root_dir)
            if relative_path.startswith('..'):
                raise ValueError(f"Prompt directory must be within root directory: {final_prompt_dir}")
        except ValueError as e:
            raise ValueError(f"Invalid prompt directory: {str(e)}")

        return root_dir, final_prompt_dir
