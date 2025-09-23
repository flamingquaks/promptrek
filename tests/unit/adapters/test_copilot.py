"""
Unit tests for Copilot adapter.
"""

import pytest

from src.apm.adapters.copilot import CopilotAdapter
from .base_test import TestAdapterBase


class TestCopilotAdapter(TestAdapterBase):
    """Test Copilot adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create Copilot adapter instance."""
        return CopilotAdapter()
    
    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "copilot"
        assert ".github/copilot-instructions.md" in adapter.file_patterns
    
    def test_supports_features(self, adapter):
        """Test feature support."""
        assert adapter.supports_variables() is True
        assert adapter.supports_conditionals() is True