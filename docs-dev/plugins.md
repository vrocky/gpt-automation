# Plugin System

GPT Automation supports plugins for custom filtering and processing.

## Built-in Plugins
- Filter plugin
- Ignore plugin
- Include-only plugin

## How Plugins Work
- Plugins are initialized and configured during `init`
- Each plugin can provide visitors for directory walking
- Plugins can filter files, modify traversal, or add logic

## Extending
- Add new plugins in `gpt_automation/plugins/`
- Register and configure as needed
