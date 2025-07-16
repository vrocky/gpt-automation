# Architecture

## Main Flow
1. CLI parses arguments (`main.py`)
2. `init` sets up config, plugins, and settings
3. `prompt` loads plugins, applies ignore/include logic, and generates output

## Key Modules
- `commands/`: CLI command implementations
- `impl/`: Core logic (directory walker, plugin loader, settings)
- `plugins/`: Built-in and custom plugins
- `resources/`: Default config and templates
- `tests/`, `test_data/`: Testing
