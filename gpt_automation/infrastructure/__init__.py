"""
Infrastructure layer — handles I/O, persistence, external concerns.

This layer implements the abstractions defined by domain layer.
It contains:
- Filesystem operations (PathProvider implementation)
- File content reading (encoding detection, error handling)
- Settings loading/saving (JSON persistence)
- Logging
- Project paths

All I/O happens in this layer. Domain never touches this code.
"""
