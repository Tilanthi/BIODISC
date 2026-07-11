"""Shared pytest fixtures and path setup for fixed_pipeline tests."""
import os
import sys

# Make biodisc_core importable from the repo root when pytest runs from root.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
