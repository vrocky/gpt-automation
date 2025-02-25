from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class PluginArgs:
    enable: bool
    ignore_filenames: List[str] = None
    include_only_filenames: List[str] = None
    back_list: List[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginArgs':
        return cls(
            enable=data.get('enable', True),
            ignore_filenames=data.get('ignore_filenames', []),
            include_only_filenames=data.get('include_only_filenames', []),
            back_list=data.get('back_list', [])
        )


@dataclass
class PluginConfig:
    plugin_name: str
    package_name: str
    args: PluginArgs

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginConfig':
        return cls(
            plugin_name=data['plugin_name'],
            package_name=data['package_name'],
            args=PluginArgs.from_dict(data.get('args', {}))
        )


@dataclass
class Settings:
    extends: str
    override: bool
    plugins: List[PluginConfig]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Settings':
        return cls(
            extends=data.get('extends', 'none'),
            override=data.get('override', False),
            plugins=[PluginConfig.from_dict(p) for p in data.get('plugins', [])]
        )
