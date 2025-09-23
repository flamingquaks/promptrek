"""
Unit tests for adapter registry.
"""

from unittest.mock import Mock

import pytest

from src.apm.adapters.base import EditorAdapter
from src.apm.adapters.registry import AdapterRegistry
from src.apm.core.exceptions import AdapterNotFoundError


class MockAdapter(EditorAdapter):
    """Mock adapter for testing."""

    def __init__(self, name="mock", description="Mock adapter", file_patterns=None):
        super().__init__(name, description, file_patterns or ["mock.txt"])

    def generate(
        self, prompt, output_dir, dry_run=False, verbose=False, variables=None
    ):
        return []

    def validate(self, prompt):
        return []


class TestAdapterRegistry:
    """Test adapter registry functionality."""

    @pytest.fixture
    def registry(self):
        """Create registry instance."""
        return AdapterRegistry()

    @pytest.fixture
    def mock_adapter(self):
        """Create mock adapter instance."""
        return MockAdapter()

    def test_register_adapter_instance(self, registry, mock_adapter):
        """Test registering adapter instance."""
        registry.register(mock_adapter)

        retrieved = registry.get("mock")
        assert retrieved == mock_adapter
        assert retrieved.name == "mock"

    def test_register_adapter_class(self, registry):
        """Test registering adapter class."""
        registry.register_class("test", MockAdapter)

        retrieved = registry.get("test")
        assert isinstance(retrieved, MockAdapter)
        # The adapter uses the default name from MockAdapter() constructor
        assert retrieved.name == "mock"

    def test_list_adapters_with_instances(self, registry, mock_adapter):
        """Test listing adapters with instances."""
        registry.register(mock_adapter)
        adapters = registry.list_adapters()

        assert "mock" in adapters

    def test_list_adapters_with_classes(self, registry):
        """Test listing adapters with classes."""
        registry.register_class("test", MockAdapter)
        adapters = registry.list_adapters()

        assert "test" in adapters

    def test_list_adapters_mixed(self, registry, mock_adapter):
        """Test listing adapters with mixed registration."""
        registry.register(mock_adapter)
        registry.register_class("test", MockAdapter)

        adapters = registry.list_adapters()
        assert "mock" in adapters
        assert "test" in adapters
        assert len(adapters) == 2

    def test_get_adapter_not_found(self, registry):
        """Test getting non-existent adapter."""
        with pytest.raises(AdapterNotFoundError):
            registry.get("nonexistent")

    def test_get_adapter_info_instance(self, registry, mock_adapter):
        """Test getting adapter info for instance."""
        registry.register(mock_adapter)

        info = registry.get_adapter_info("mock")
        assert info["name"] == "mock"
        assert info["description"] == "Mock adapter"
        assert info["file_patterns"] == ["mock.txt"]
        assert info["status"] == "available"

    def test_get_adapter_info_class(self, registry):
        """Test getting adapter info for class."""

        class TestAdapter(MockAdapter):
            _description = "Test Description"
            _file_patterns = ["test.txt"]

        registry.register_class("test", TestAdapter)

        info = registry.get_adapter_info("test")
        assert info["name"] == "test"
        assert info["description"] == "Test Description"
        assert info["file_patterns"] == ["test.txt"]
        assert info["status"] == "available"

    def test_get_adapter_info_not_found(self, registry):
        """Test getting info for non-existent adapter."""
        with pytest.raises(AdapterNotFoundError):
            registry.get_adapter_info("nonexistent")

    def test_lazy_instantiation(self, registry):
        """Test that adapter classes are instantiated lazily."""
        registry.register_class("lazy", MockAdapter)

        # First call should instantiate
        adapter1 = registry.get("lazy")
        # Second call should return same instance
        adapter2 = registry.get("lazy")

        assert adapter1 is adapter2
