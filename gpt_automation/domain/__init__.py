"""
Domain layer — pure business logic with no I/O or external dependencies.

This is the core of the application. It contains:
- Business rules (what files should be included/excluded)
- Core abstractions (FileFilter, DirectoryReader, FileContent)
- Use case logic (no I/O calls)

The domain layer is independently testable and has zero dependencies on:
- Filesystem operations
- JSON files or settings
- Logging frameworks
- CLI arguments
"""
