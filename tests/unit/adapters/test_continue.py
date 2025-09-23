"""
Unit tests for Continue adapter.
"""

import json
from pathlib import Path
import pytest
from unittest.mock import patch, mock_open

from src.apm.adapters.continue_adapter import ContinueAdapter
from src.apm.core.models import UniversalPrompt, PromptMetadata
from src.apm.core.exceptions import ValidationError
from .base_test import TestAdapterBase


class TestContinueAdapter(TestAdapterBase):
    """Test Continue editor adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create Continue adapter instance."""
        return ContinueAdapter()
    
    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "continue"
        assert adapter.description == "Continue (.continue/config.json)"
        assert adapter.file_patterns == [".continue/config.json"]
    
    def test_supports_variables(self, adapter):
        """Test variable support."""
        assert adapter.supports_variables() is True
    
    def test_supports_conditionals(self, adapter):
        """Test conditional support."""
        assert adapter.supports_conditionals() is True
    
    def test_validate_valid_prompt(self, adapter, sample_prompt):
        """Test validation of valid prompt."""
        errors = adapter.validate(sample_prompt)
        assert len(errors) == 0
    
    def test_validate_missing_description(self, adapter):
        """Test validation with missing description."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="",  # Empty description
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01"
            ),
            targets=["continue"]
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 1
        assert errors[0].field == "metadata.description"
    
    def test_build_content(self, adapter, sample_prompt):
        """Test content generation."""
        content = adapter._build_content(sample_prompt)
        
        # Parse as JSON to verify structure
        config = json.loads(content)
        
        assert "models" in config
        assert "systemMessage" in config
        assert "completionOptions" in config
        assert "allowAnonymousTelemetry" in config
        
        assert sample_prompt.metadata.title in config["systemMessage"]
        assert sample_prompt.metadata.description in config["systemMessage"]
        assert "General Instructions:" in config["systemMessage"]
        
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_actual_files(self, mock_mkdir, mock_file, adapter, sample_prompt):
        """Test actual file generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)
        
        assert len(files) == 1
        assert files[0] == output_dir / ".continue" / "config.json"
        mock_mkdir.assert_called_once()
        mock_file.assert_called_once()
    
    def test_generate_dry_run(self, adapter, sample_prompt, capsys):
        """Test dry run generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=True)
        
        captured = capsys.readouterr()
        assert "Would create" in captured.out
        assert len(files) == 1