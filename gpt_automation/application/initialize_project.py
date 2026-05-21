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

    Dependencies are all injected — no direct filesystem calls from this class.
    """

    def __init__(
        self,
        filter_builder: FilterBuilder,
        logger: Logger,
        resources_dir: Path,
    ):
        self._filter_builder = filter_builder
        self._logger = logger
        self._resources_dir = resources_dir

    def run(self, project_root: Path, profiles: list[str]) -> bool:
        """
        Fully initialize the project. Returns True on success.

        Steps:
          1. Create .gpt/ directory structure
          2. Write default settings.json
          3. Copy .gitignore template
          4. Create plugin data files (blocklist, allowlist, etc.)
        """
        try:
            self._logger.info(f"Initializing project: {project_root}")
            paths = ProjectPaths(project_root)

            self._create_directories(paths)
            self._write_default_settings(paths)
            self._copy_gitignore_template(paths)
            self._setup_plugin_files(paths, profiles)

            self._logger.info("Project ready")
            return True

        except Exception as e:
            self._logger.exception(e, "Initialization failed")
            return False

    # ─────────────────────────── steps ───────────────────────────

    def _create_directories(self, paths: ProjectPaths) -> None:
        for directory in paths.all_required_directories():
            directory.mkdir(parents=True, exist_ok=True)
        self._logger.debug("Directories ready")

    def _write_default_settings(self, paths: ProjectPaths) -> None:
        if paths.settings_file.exists():
            self._logger.debug("Settings file already exists — skipping")
            return

        writer = SettingsWriter(paths.settings_file)
        writer.write(ProjectSettings.defaults())
        self._logger.debug(f"Wrote default settings to {paths.settings_file}")

    def _copy_gitignore_template(self, paths: ProjectPaths) -> None:
        template = self._resources_dir / '.gitignore_template'
        destination = paths.gpt_dir / '.gitignore'

        if destination.exists() or not template.exists():
            return

        copyfile(template, destination)
        self._logger.debug(f"Copied .gitignore template to {destination}")

    def _setup_plugin_files(self, paths: ProjectPaths, profiles: list[str]) -> None:
        self._filter_builder.setup_plugin_files(paths.root, profiles)
        self._logger.debug("Plugin files ready")
