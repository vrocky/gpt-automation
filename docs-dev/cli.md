# CLI Usage

## Installation
- Recommended: `pipx install gpt-automation`
- Manual: `python setup.py install`

## Commands
### `init`
Initializes `.gpt` config directory and sample ignore/include files.
```
autogpt init [profile names]
```

### `prompt`
Generates prompt for directory structure and/or file contents.
```
autogpt prompt --dir [profiles] --content [profiles]
```
- `--dir`: Directory structure only
- `--content`: File contents only
- Both: Full prompt
- Output is copied to clipboard
