"""
Unit tests for Tabnine adapter.
"""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from promptrek.adapters.tabnine import TabnineAdapter

from .base_test import TestAdapterBase


class TestTabnineAdapter(TestAdapterBase):
    """Test Tabnine adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Tabnine adapter instance."""
        return TabnineAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "tabnine"
        assert "Tabnine" in adapter.description
        assert ".tabnine_commands" in adapter.file_patterns

    def test_supports_variables(self, adapter):
        """Test variable support."""
        assert adapter.supports_variables() is True

    def test_supports_conditionals(self, adapter):
        """Test conditional support."""
        assert adapter.supports_conditionals() is True

    def test_validate_valid_prompt(self, adapter, sample_prompt):
        """Test validation of valid prompt."""
        errors = adapter.validate(sample_prompt)
        # Should only have warnings, no critical errors
        assert all(error.severity == "warning" for error in errors)

    @patch("builtins.open", new_callable=mock_open)
    def test_generate_actual_files(self, mock_file, adapter, sample_prompt):
        """Test actual file generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)

        assert len(files) == 1
        assert files[0] == output_dir / ".tabnine_commands"
        assert mock_file.called

    def test_generate_dry_run(self, adapter, sample_prompt, capsys):
        """Test dry run generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=True)

        captured = capsys.readouterr()
        assert "Would create" in captured.out
        assert len(files) == 1
        assert files[0] == output_dir / ".tabnine_commands"
