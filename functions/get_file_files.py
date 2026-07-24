"""Backward-compatible import for the accidentally misnamed module."""

from functions.write_file import write_file

__all__ = ["write_file"]
