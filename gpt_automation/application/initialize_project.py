"""
Use case: Initialize a new project.

Story: "Set up a project with .gpt/ directory, default settings, and plugin files."
"""

from pathlib import Path
from shutil import copyfile

from gpt_automation.infrastructure.filesystem.project_paths import ProjectPaths
from gpt_automation.infrastructure.config.settings_model import ProjectSettings
from gpt_automation.infrastructure.config.settings_loader import SettingsWriter
from gpt_automation.infrastructure.plugins.filter_builder import FilterBuilder
from gpt_automation.infrastructure.logging.logger import Logger


class InitializeProject:
    """
    Initialize a project directory for use with gpt_automation.

    Creates .gpt/ directory structure, writes default settings, copies
    template files, and initializes any plugin-managed files.

    All dependencies are injected — no hidden object construction:
    - paths: manages .gpt/ directory paths
    - settings_writer: writes settings.json
    - filter_builder: initializes plugin files
    - logger: logs progress
    - resources_dir: location of template files (.gitignore_template, etc.)
    """

    def __init__(
        self,
        paths: ProjectPaths,
        settings_writer: SettingsWriter,
        filter_builder: FilterBuilder,
        logger: Logger,
        resources_dir: Path,
    ):
        self._paths = paths
        self._settings_writer = settings_writer
        self._filter_builder = filter_builder
        self._logger = logger
        self._resources_dir = resources_dir

    def run(self, profiles: list[str]) -> bool:
        """
        Fully initialize the project. Returns True on success.

        Steps:
          1. Create .gpt/ directory structure
          2. Write default settings.json
          3. Copy .gitignore template
          4. Create plugin data files (blocklist, allowlist, etc.)
        """
        try:
            self._logger.info(f"Initializing project: {self._paths.root}")

            self._create_directories()
            self._write_default_settings()
            self._copy_gitignore_template()
            self._setup_plugin_files(profiles)

            self._logger.info("Project ready")
            return True

        except Exception as e:
            self._logger.exception(e, "Initialization failed")
            return False

    # ─────────────────────────── steps ───────────────────────────

    def _create_directories(self) -> None:
        """Create all required .gpt/ subdirectories."""
        for directory in self._paths.all_required_directories():
            directory.mkdir(parents=True, exist_ok=True)
        self._logger.debug("Directories ready")

    def _write_default_settings(self) -> None:
        """Create default settings.json if it doesn't exist."""
        if self._paths.settings_file.exists():
            self._logger.debug("Settings file already exists — skipping")
            return

        self._settings_writer.write(ProjectSettings.defaults())
        self._logger.debug(f"Wrote default settings to {self._paths.settings_file}")

    def _copy_gitignore_template(self) -> None:
        """Copy .gitignore template if it exists."""
        template = self._resources_dir / '.gitignore_template'
        destination = self._paths.gpt_dir / '.gitignore'

        if destination.exists() or not template.exists():
            return

        copyfile(template, destination)
        self._logger.debug(f"Copied .gitignore template to {destination}")

    def _setup_plugin_files(self, profiles: list[str]) -> None:
        """Initialize plugin-managed files (blocklist, allowlist, etc.)."""
        self._filter_builder.setup_plugin_files(self._paths.root, profiles)
        self._logger.debug("Plugin files ready")
