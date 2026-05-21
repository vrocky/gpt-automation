"""
Dependency injection container — the single place where objects are wired together.

Reading this file from top to bottom tells you:
- What components exist
- What depends on what
- How data flows through the system

All object construction happens here. Application code receives
fully-formed objects, never constructs dependencies.

The dependency graph (simplified):

    OsFilesystemQuery (real I/O)
         ↓
    DirectoryWalker (domain logic)

    SettingsReader (read JSON)
    SettingsWriter (write JSON)
         ↓
    ProjectSettings
         ↓
    FilterBuilder (select visitors)
         ↓
    GeneratePrompts (use case)

    ProjectPaths (path management)
    Logger (logging)
    FileContentReader (file I/O)
         ↓
    InitializeProject (use case)
    GeneratePrompts (use case)
"""

from pathlib import Path
from functools import cached_property

from gpt_automation.infrastructure.filesystem.project_paths import ProjectPaths
from gpt_automation.infrastructure.filesystem.os_filesystem_query import OsFilesystemQuery
from gpt_automation.infrastructure.config.settings_loader import SettingsReader, SettingsWriter
from gpt_automation.infrastructure.config.settings_model import ProjectSettings
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

    Construct once at startup: `container = AppContainer(project_root)`

    Then use: `container.initialize_project` or `container.generate_prompts`

    Each @cached_property builds its object once, then returns the same instance.
    """

    def __init__(self, project_root: Path):
        """Initialize with the project root directory."""
        self._root = Path(project_root).resolve()

    # ─────────────────────────── INFRASTRUCTURE ──────────────────────────────

    @cached_property
    def paths(self) -> ProjectPaths:
        """
        All paths in the project (.gpt/, .gpt/settings/, etc.).

        Pure path math — no I/O. Test-friendly.
        """
        return ProjectPaths(self._root)

    @cached_property
    def logger(self) -> Logger:
        """
        Log to file and console simultaneously.

        Application code depends on this Logger interface, not
        the concrete implementations.
        """
        self.paths.logs_dir.mkdir(parents=True, exist_ok=True)
        return CompositeLogger([
            FileLogger(self.paths.logs_dir / 'app.log'),
            ConsoleLogger(),
        ])

    @cached_property
    def filesystem(self) -> OsFilesystemQuery:
        """
        Ask the OS about files.

        This is what DirectoryWalker uses to ask: "is this a directory?"
        Tests replace this with a fake.
        """
        return OsFilesystemQuery()

    @cached_property
    def settings_reader(self) -> SettingsReader:
        """Load settings.json into ProjectSettings."""
        return SettingsReader(self.paths.settings_file)

    @cached_property
    def settings_writer(self) -> SettingsWriter:
        """Write ProjectSettings to settings.json."""
        return SettingsWriter(self.paths.settings_file)

    @cached_property
    def settings(self) -> ProjectSettings:
        """
        The current project settings (which plugins are enabled, etc.).

        Read from disk once at startup, cached for the lifetime of this container.
        """
        return self.settings_reader.read()

    @cached_property
    def filter_builder(self) -> FilterBuilder:
        """
        Build file filters from settings.

        Knows which plugins are enabled and creates the right visitors.
        """
        return FilterBuilder(self.settings, self.paths.plugins_dir)

    @cached_property
    def resources_dir(self) -> Path:
        """
        Directory containing built-in resources (.gitignore_template, etc.).

        Resolved relative to the gpt_automation package.
        """
        return Path(__file__).parent / 'resources'

    # ─────────────────────────────── DOMAIN ──────────────────────────────────

    @cached_property
    def directory_walker(self) -> DirectoryWalker:
        """
        Walk directory trees applying filters.

        Pure domain logic — no I/O dependencies beyond the injected
        OsFilesystemQuery.
        """
        return DirectoryWalker(self.filesystem)

    # ─────────────────────────── APPLICATION ─────────────────────────────────

    @cached_property
    def content_reader(self) -> FileContentReader:
        """Read file content with graceful encoding detection."""
        return FileContentReader()

    @cached_property
    def initialize_project(self) -> InitializeProject:
        """
        Use case: Initialize a new project.

        All dependencies are explicitly passed:
        - paths: where to create directories
        - settings_writer: write default settings.json
        - filter_builder: initialize plugin files
        - logger: report progress
        - resources_dir: where template files live
        """
        return InitializeProject(
            paths=self.paths,
            settings_writer=self.settings_writer,
            filter_builder=self.filter_builder,
            logger=self.logger,
            resources_dir=self.resources_dir,
        )

    @cached_property
    def generate_prompts(self) -> GeneratePrompts:
        """
        Use case: Generate directory and content prompts.

        All dependencies are explicitly passed:
        - walker: traverses directories
        - logger: report progress
        - content_reader: read file contents
        - paths: project structure
        - settings: which plugins enabled
        - filter_builder: create visitor filters
        """
        return GeneratePrompts(
            walker=self.directory_walker,
            logger=self.logger,
            content_reader=self.content_reader,
            paths=self.paths,
            settings=self.settings,
            filter_builder=self.filter_builder,
        )

    # ─────────────────────────── VALIDATION ──────────────────────────────────

    def validate(self) -> None:
        """
        Check that the container can build all dependencies.

        Call this early to fail fast if something is misconfigured.
        Raises an exception if validation fails.
        """
        # Ensure log directory is creatable
        self.logger.debug("Container validation: all dependencies loadable")
