"""
Unit tests for Cursor adapter.
"""

import pytest

from src.promptrek.adapters.cursor import CursorAdapter

from .base_test import TestAdapterBase


class TestCursorAdapter(TestAdapterBase):
    """Test Cursor adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Cursor adapter instance."""
        return CursorAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "cursor"
        assert ".cursorrules" in adapter.file_patterns

    def test_supports_features(self, adapter):
        """Test feature support."""
        assert adapter.supports_variables() is True
        assert adapter.supports_conditionals() is True
