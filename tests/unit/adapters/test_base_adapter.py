"""Tests for base adapter functionality."""

import pytest
from pathlib import Path
from promptrek.adapters.base import EditorAdapter
from promptrek.core.models import UniversalPrompt, UniversalPromptV2, PromptMetadata, Instructions


class MockAdapter(EditorAdapter):
    """Mock adapter for testing base functionality."""
    
    def __init__(self):
        super().__init__(
            name="mock",
            description="Mock adapter for testing",
            file_patterns=["*.mock"]
        )
    
    def generate(self, prompt, output_dir, **kwargs):
        return []
    
    def validate(self, prompt):
        return []


class TestEditorAdapterBase:
    """Test base EditorAdapter functionality."""

    @pytest.fixture
    def adapter(self):
        return MockAdapter()

    def test_adapter_properties(self, adapter):
        """Test adapter basic properties."""
        assert adapter.name == "mock"
        assert adapter.description == "Mock adapter for testing"
        assert adapter.file_patterns == ["*.mock"]

    def test_adapter_name_normalization(self, adapter):
        """Test that adapter name is normalized."""
        assert adapter.name.islower()
        assert " " not in adapter.name

    def test_validate_returns_list(self, adapter):
        """Test that validate always returns a list."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test"
        )
        
        result = adapter.validate(prompt)
        
        assert isinstance(result, list)

    def test_generate_returns_list(self, adapter, tmp_path):
        """Test that generate returns a list of paths."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test"
        )
        
        result = adapter.generate(prompt, tmp_path)
        
        assert isinstance(result, list)

    def test_substitute_variables_exists(self, adapter):
        """Test that substitute_variables method exists."""
        assert hasattr(adapter, 'substitute_variables')
        assert callable(adapter.substitute_variables)

    def test_adapter_repr(self, adapter):
        """Test adapter string representation."""
        repr_str = repr(adapter)
        assert "mock" in repr_str.lower()

    def test_file_patterns_list(self, adapter):
        """Test file patterns is a list."""
        assert isinstance(adapter.file_patterns, list)
        assert len(adapter.file_patterns) > 0
