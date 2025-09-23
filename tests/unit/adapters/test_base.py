"""
Unit tests for base adapter functionality.
"""

import pytest

from src.apm.adapters.continue_adapter import ContinueAdapter
from src.apm.core.models import UniversalPrompt

from .base_test import TestAdapterBase


class TestBaseAdapter(TestAdapterBase):
    """Test base adapter functionality."""

    @pytest.fixture
    def adapter(self):
        """Create concrete adapter for testing base functionality."""
        return ContinueAdapter()

    def test_get_required_variables(self, adapter, sample_prompt):
        """Test getting required variables."""
        # Base implementation returns empty list
        required = adapter.get_required_variables(sample_prompt)
        assert isinstance(required, list)

    def test_substitute_variables(self, adapter, sample_prompt):
        """Test variable substitution."""
        # Test that substitution works with variables
        variables = {"extra_var": "extra_value"}
        processed = adapter.substitute_variables(sample_prompt, variables)

        assert isinstance(processed, UniversalPrompt)
        assert processed.schema_version == sample_prompt.schema_version

    def test_substitute_variables_no_support(self, sample_prompt):
        """Test variable substitution when not supported."""

        # Create adapter that doesn't support variables
        class NoVariablesAdapter(ContinueAdapter):
            def supports_variables(self):
                return False

        adapter = NoVariablesAdapter()
        processed = adapter.substitute_variables(sample_prompt, {"var": "value"})

        # Should return original prompt unchanged
        assert processed == sample_prompt
