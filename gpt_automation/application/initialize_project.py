"""
Use case: Initialize a new project.

Story: "As a user, I want to set up a new project with .gpt/ directory and default settings."
"""

from pathlib import Path

from gpt_automation.domain.traversal.directory_reader import PathProvider
from gpt_automation.infrastructure.filesystem.project_paths import ProjectPaths
from gpt_automation.infrastructure.config.settings_model import Settings
from gpt_automation.infrastructure.config.settings_loader import SettingsSaver
from gpt_automation.infrastructure.logging.logger import Logger


class InitializeProject:
    """
    Initialize a new project with .gpt/ directory and settings.

    Dependencies injected:
    - path_provider: For filesystem operations (abstraction)
    - logger: For logging (abstraction)
    """

    def __init__(self, path_provider: PathProvider, logger: Logger):
        self._path_provider = path_provider
        self._logger = logger

    def execute(self, project_root: Path, profile_names: list[str]) -> bool:
        """
        Initialize project.

        Returns True if successful, False otherwise.
        """
        try:
            self._logger.info(f"Initializing project at {project_root}")

            paths = ProjectPaths(project_root)

            # Step 1: Create all required directories
            self._create_directories(paths)

            # Step 2: Create default settings file
            self._create_settings_file(paths)

            # Step 3: Initialize plugins (they may create files)
            self._initialize_plugins(paths, profile_names)

            self._logger.info("Project initialized successfully")
            return True

        except Exception as e:
            self._logger.exception(e, "Initialization failed")
            return False

    def _create_directories(self, paths: ProjectPaths) -> None:
        """Create all required .gpt/ directories."""
        self._logger.debug("Creating directories...")

        for directory in paths.all_required_directories():
            if not self._path_provider.is_directory(directory):
                Path(directory).mkdir(parents=True, exist_ok=True)
                self._logger.debug(f"Created {directory}")

    def _create_settings_file(self, paths: ProjectPaths) -> None:
        """Create default settings.json."""
        self._logger.debug("Creating settings file...")

        if paths.settings_file.exists():
            self._logger.debug("Settings file already exists")
            return

        settings = Settings.defaults()
        saver = SettingsSaver(paths.settings_file)
        saver.save(settings)
        self._logger.debug(f"Created settings file at {paths.settings_file}")

    def _initialize_plugins(self, paths: ProjectPaths, profile_names: list[str]) -> None:
        """Initialize plugins that need setup (e.g., create blacklist/whitelist files)."""
        self._logger.debug(f"Initializing plugins for profiles: {profile_names}")

        # TODO: Plugin initialization will be implemented in integration layer
        pass
