# linux_cop/__init__.py
"""
Linux Copilot
~~~~~~~~~~~~~
A modular, terminal-native AI agent framework.

Project structure:
- cli/      → Command line entrypoints
- core/     → Agents, tools, and utilities
- docs/     → Prompts and documentation
- config/   → Credentials and settings
- logs/     → Runtime history
"""
import sys
sys.dont_write_bytcode=False

__title__ = "linux_cop"
__version__ = "0.1.0"
__author__ = "tunahanyrd"
__license__ = "MIT"
__all__ = ["cli", "core", "config", "docs", "logs"]
