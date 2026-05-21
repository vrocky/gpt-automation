"""
Dependency injection container — the single place where objects are wired together.

Reading this file tells you the entire shape of the application:
what exists, what depends on what, and how it all connects.
"""

from pathlib import Path
from functools import cached_property

from gpt_automation.infrastructure.filesystem.project_paths import ProjectPaths
from gpt_automation.infrastructure.filesystem.os_filesystem_query import OsFilesystemQuery
from gpt_automation.infrastructure.config.settings_loader import SettingsReader
from gpt_automation.infrastructure.plugins.filter_builder import FilterBuilder
from gpt_automation.infrastructure.logging.logger import (
    Logger,
    FileLogger,
    ConsoleLogger,
    CompositeLogger,
)
from gpt_automation.domain.traversal.directory_reader import DirectoryWalker
from gpt_automation.application.initialize_project import InitializeProject
from gpt_automation.application.generate_prompts import GeneratePrompts, FileContentReader


class AppContainer:
    """
    Build and cache every object the application needs.

    Construct once at startup. Pass `project_root` so all paths are relative
    to the same root directory.
    """

    def __init__(self, project_root: Path):
        self._root = Path(project_root).resolve()

    # ─────────────────────── infrastructure ──────────────────────────

    @cached_property
    def paths(self) -> ProjectPaths:
        return ProjectPaths(self._root)

    @cached_property
    def logger(self) -> Logger:
        """Log to both file and console."""
        self.paths.logs_dir.mkdir(parents=True, exist_ok=True)
        return CompositeLogger([
            FileLogger(self.paths.logs_dir / 'app.log'),
            ConsoleLogger(),
        ])

    @cached_property
    def filesystem(self) -> OsFilesystemQuery:
        return OsFilesystemQuery()

    @cached_property
    def settings(self):
        return SettingsReader(self.paths.settings_file).read()

    @cached_property
    def filter_builder(self) -> FilterBuilder:
        return FilterBuilder(self.settings, self.paths.plugins_dir)

    # ─────────────────────────── domain ──────────────────────────────

    @cached_property
    def directory_walker(self) -> DirectoryWalker:
        return DirectoryWalker(self.filesystem)

    # ─────────────────────── application ─────────────────────────────

    @cached_property
    def initialize_project(self) -> InitializeProject:
        resources_dir = Path(__file__).parent / 'resources'
        return InitializeProject(
            filter_builder=self.filter_builder,
            logger=self.logger,
            resources_dir=resources_dir,
        )

    @cached_property
    def generate_prompts(self) -> GeneratePrompts:
        return GeneratePrompts(
            walker=self.directory_walker,
            logger=self.logger,
            content_reader=FileContentReader(),
        )
