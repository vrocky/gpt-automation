"""
Project path management (pure path math, no I/O).

Single source of truth for where everything lives in .gpt/ directory.
"""

from pathlib import Path


class ProjectPaths:
    """
    Manages all paths within a project.

    Pure path math—no filesystem operations.
    All directory paths are computed from root_dir.
    """

    def __init__(self, project_root: Path):
        self._root = Path(project_root).resolve()

    @property
    def root(self) -> Path:
        """Project root directory."""
        return self._root

    @property
    def gpt_dir(self) -> Path:
        """Main .gpt directory."""
        return self._root / '.gpt'

    @property
    def settings_dir(self) -> Path:
        """Directory containing settings files."""
        return self.gpt_dir / 'settings'

    @property
    def settings_file(self) -> Path:
        """Path to base_settings.json."""
        return self.settings_dir / 'base_settings.json'

    @property
    def config_dir(self) -> Path:
        """Directory for configuration files."""
        return self.gpt_dir / 'conf'

    @property
    def plugins_dir(self) -> Path:
        """Directory for plugin configurations."""
        return self.gpt_dir / 'config'

    @property
    def logs_dir(self) -> Path:
        """Directory for log files."""
        return self.gpt_dir / 'logs'

    def plugin_dir(self, plugin_name: str) -> Path:
        """Get directory for a specific plugin."""
        return self.plugins_dir / plugin_name

    def all_required_directories(self) -> list[Path]:
        """List all directories that must exist for project to work."""
        return [
            self.gpt_dir,
            self.settings_dir,
            self.config_dir,
            self.plugins_dir,
            self.logs_dir,
        ]
