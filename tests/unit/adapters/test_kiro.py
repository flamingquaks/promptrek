"""
Unit tests for Kiro adapter.
"""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.apm.adapters.kiro import KiroAdapter
from .base_test import TestAdapterBase


class TestKiroAdapter(TestAdapterBase):
    """Test Kiro adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Kiro adapter instance."""
        return KiroAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "kiro"
        assert "Kiro" in adapter.description
        assert ".kiro/config.json" in adapter.file_patterns
        assert ".kiro/prompts.md" in adapter.file_patterns

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

    def test_build_config_content(self, adapter, sample_prompt):
        """Test config generation."""
        content = adapter._build_config(sample_prompt)
        
        # Parse as JSON to verify structure
        config = json.loads(content)
        
        assert "name" in config
        assert "description" in config
        assert "settings" in config
        assert config["name"] == sample_prompt.metadata.title

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_actual_files(self, mock_mkdir, mock_file, adapter, sample_prompt):
        """Test actual file generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)

        assert len(files) == 2
        assert any(".kiro/config.json" in str(f) for f in files)
        assert any(".kiro/prompts.md" in str(f) for f in files)
        assert mock_mkdir.call_count == 1
        assert mock_file.call_count == 2

    def test_generate_dry_run(self, adapter, sample_prompt, capsys):
        """Test dry run generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=True)

        captured = capsys.readouterr()
        assert "Would create" in captured.out
        assert len(files) == 2