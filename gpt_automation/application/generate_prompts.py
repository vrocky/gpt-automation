"""
Use case: Generate directory-structure and file-content prompts.

Story: "Walk a directory, filter out irrelevant files, format results as
a prompt that can be fed to a language model."
"""

from pathlib import Path
from dataclasses import dataclass

from gpt_automation.domain.traversal.directory_reader import DirectoryWalker
from gpt_automation.infrastructure.filesystem.project_paths import ProjectPaths
from gpt_automation.infrastructure.config.settings_model import ProjectSettings
from gpt_automation.infrastructure.plugins.filter_builder import FilterBuilder
from gpt_automation.infrastructure.logging.logger import Logger


@dataclass
class PromptResult:
    """
    The output of a prompt generation run.

    Both fields are empty strings when nothing was generated.
    """
    directory_tree: str   # Formatted directory-structure block
    file_contents: str    # Formatted file-content block


class GeneratePrompts:
    """
    Walk a directory and generate LLM-ready prompts.

    All dependencies are injected:
    - walker: traverses directory, applies filters
    - logger: logs progress/errors
    - content_reader: reads file contents with encoding handling
    - paths: project directory structure
    - settings: which plugins are enabled
    - filter_builder: creates visitor filters from settings

    This use case has NO hidden construction — everything comes in.
    """

    def __init__(
        self,
        walker: DirectoryWalker,
        logger: Logger,
        content_reader: 'FileContentReader',
        paths: ProjectPaths,
        settings: ProjectSettings,
        filter_builder: FilterBuilder,
    ):
        self._walker = walker
        self._logger = logger
        self._content_reader = content_reader
        self._paths = paths
        self._settings = settings
        self._filter_builder = filter_builder

    def run(
        self,
        work_dir: Path,
        profiles: list[str],
        include_tree: bool = True,
        include_contents: bool = True,
    ) -> PromptResult:
        """
        Generate prompts for the given directory and profiles.

        work_dir     – directory to analyse
        profiles     – list of profile names (empty list = default profile)
        include_tree – whether to include directory structure
        include_contents – whether to include file contents
        """
        self._logger.info(f"Generating prompts for {work_dir} (profiles={profiles})")

        # Build filter from settings
        file_filter = self._filter_builder.build_for_traversal(
            self._paths.root,
            work_dir,
            profiles,
        )

        # Collect matching files
        files = self._walker.collect_matching_files(work_dir, file_filter)
        self._logger.info(f"Collected {len(files)} files after filtering")

        # Format output blocks
        tree_block = self._build_tree(files, self._paths.root) if include_tree else ''
        content_block = self._build_contents(files) if include_contents else ''

        return PromptResult(directory_tree=tree_block, file_contents=content_block)

    # ────────────────────────── formatting ───────────────────────────

    def _build_tree(self, files: list[Path], root: Path) -> str:
        """Format files as a nested directory-tree string."""
        if not files:
            return ''

        lines = ['Directory structure:', '']
        tree: dict = {}

        for file_path in sorted(files):
            try:
                rel = file_path.relative_to(root)
            except ValueError:
                rel = file_path

            node = tree
            for part in rel.parts[:-1]:
                node = node.setdefault(part, {})
            node[rel.parts[-1]] = None

        self._render_tree(tree, lines, prefix='')
        return '\n'.join(lines)

    def _render_tree(self, node: dict, lines: list[str], prefix: str) -> None:
        """Recursively render tree dict into lines."""
        items = sorted(node.items())
        for i, (name, children) in enumerate(items):
            connector = '└── ' if i == len(items) - 1 else '├── '
            lines.append(f"{prefix}{connector}{name}")

            if isinstance(children, dict):
                extension = '    ' if i == len(items) - 1 else '│   '
                self._render_tree(children, lines, prefix + extension)

    def _build_contents(self, files: list[Path]) -> str:
        """Format file contents as annotated blocks."""
        if not files:
            return ''

        blocks: list[str] = []
        for file_path in sorted(files):
            content = self._content_reader.read(file_path)
            blocks.append(f"### {file_path}\n{content}")

        return '\n\n'.join(blocks)


class FileContentReader:
    """Read a file's text content, handling encoding gracefully."""

    def read(self, file_path: Path) -> str:
        """Return file content as a string, or a placeholder on error."""
        try:
            return self._detect_and_read(file_path)
        except Exception as e:
            return f'[Could not read {file_path.name}: {e}]'

    def _detect_and_read(self, file_path: Path) -> str:
        """Try chardet encoding detection, fall back to utf-8 with replacement."""
        raw = file_path.read_bytes()
        if not raw:
            return ''

        try:
            import chardet
            detected = chardet.detect(raw)
            encoding = detected.get('encoding') or 'utf-8'
            return raw.decode(encoding, errors='replace')
        except ImportError:
            return raw.decode('utf-8', errors='replace')
