# GPT Automation: Project Overview

GPT Automation is a Python CLI tool for generating project prompts (directory structure and file contents) for LLMs or automation workflows. It features advanced file inclusion/exclusion logic, profile support, and a plugin system.

## Key Features
- Prompt generation (directory, content, or both)
- Profile-based configuration for flexible scenarios
- Early directory exclusion for performance
- Extensible via plugins
- Output copied to clipboard in LLM-friendly format

## Main Components
- CLI entrypoint: `main.py`
- Commands: `init` and `prompt`
- Directory walking and filtering logic
- Plugin system for extensibility
- Settings and profile management
- Comprehensive documentation and test suite
