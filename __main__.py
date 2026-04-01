"""
tracefix/__main__.py

Allows running tracefix as a module:
    python -m tracefix install
    python -m tracefix uninstall
    python -m tracefix status
    python -m tracefix run <file>
    python -m tracefix check <file>
    python -m tracefix tracefix "<error message>"

After install, the hook is active automatically on every Python run —
no need to call anything again.
"""

from .cli_i import app

if __name__ == "__main__":
    app()