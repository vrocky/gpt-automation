# Developer Notes

- Use `setuptools` for packaging; see `setup.py`
- All JSON, TXT, and resource files are included in the package
- Logging is used throughout for debugging and error reporting
- Encoding detection is used when reading files for prompt content
- Plugins must implement initialization, configuration, and visitor logic
