"""Unit tests for adapter registry."""

from pathlib import Path
from typing import Dict, List, Optional

import pytest

from promptrek.adapters.base import EditorAdapter
from promptrek.adapters.registry import AdapterCapability, AdapterRegistry
from promptrek.core.exceptions import AdapterNotFoundError
from promptrek.core.models import UniversalPrompt, UniversalPromptV2, UniversalPromptV3


class MockAdapter(EditorAdapter):
    """Mock adapter for testing."""

    def __init__(self, name: str = "mock", description: str = "Mock adapter"):
        super().__init__(name=name, description=description, file_patterns=["test.md"])

    def generate(
        self,
        prompt: UniversalPrompt | UniversalPromptV2 | UniversalPromptV3,
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, str]] = None,
    ) -> List[Path]:
        """Mock generate method."""
        return []

    def validate(
        self, prompt: UniversalPrompt | UniversalPromptV2 | UniversalPromptV3
    ) -> List[str]:
        """Mock validate method."""
        return []


class TestAdapterRegistry:
    """Tests for AdapterRegistry."""

    def test_register_adapter_with_capabilities(self):
        """Test registering adapter with capabilities."""
        registry = AdapterRegistry()

        adapter = MockAdapter(name="test", description="Test adapter")
        capabilities = [
            AdapterCapability.GENERATES_PROJECT_FILES,
            AdapterCapability.SUPPORTS_VARIABLES,
        ]

        registry.register(adapter, capabilities)

        assert "test" in registry.list_adapters()
        assert registry.has_capability(
            "test", AdapterCapability.GENERATES_PROJECT_FILES
        )
        assert registry.has_capability("test", AdapterCapability.SUPPORTS_VARIABLES)

    def test_register_adapter_without_capabilities(self):
        """Test registering adapter without capabilities."""
        registry = AdapterRegistry()

        adapter = MockAdapter(name="test2", description="Test adapter 2")
        # Register without capabilities
        registry.register(adapter, None)

        assert "test2" in registry.list_adapters()
        # Should not have any capabilities
        assert not registry.has_capability(
            "test2", AdapterCapability.GENERATES_PROJECT_FILES
        )

    def test_get_adapters_by_capability(self):
        """Test getting adapters by capability."""
        registry = AdapterRegistry()

        adapter1 = MockAdapter(name="adapter1", description="Adapter 1")
        adapter2 = MockAdapter(name="adapter2", description="Adapter 2")

        registry.register(adapter1, [AdapterCapability.GENERATES_PROJECT_FILES])
        registry.register(adapter2, [AdapterCapability.GLOBAL_CONFIG_ONLY])

        project_adapters = registry.get_adapters_by_capability(
            AdapterCapability.GENERATES_PROJECT_FILES
        )
        assert "adapter1" in project_adapters
        assert "adapter2" not in project_adapters

        global_adapters = registry.get_adapters_by_capability(
            AdapterCapability.GLOBAL_CONFIG_ONLY
        )
        assert "adapter2" in global_adapters
        assert "adapter1" not in global_adapters

    def test_has_capability(self):
        """Test checking if adapter has capability."""
        registry = AdapterRegistry()

        adapter = MockAdapter(name="test", description="Test")
        registry.register(adapter, [AdapterCapability.GENERATES_PROJECT_FILES])

        assert registry.has_capability(
            "test", AdapterCapability.GENERATES_PROJECT_FILES
        )
        assert not registry.has_capability("test", AdapterCapability.GLOBAL_CONFIG_ONLY)
        # Non-existent adapter should return False
        assert not registry.has_capability(
            "nonexistent", AdapterCapability.GENERATES_PROJECT_FILES
        )

    def test_get_project_file_adapters(self):
        """Test getting project file adapters."""
        registry = AdapterRegistry()

        project = MockAdapter(name="project", description="Project adapter")
        global_adapter = MockAdapter(name="global", description="Global adapter")

        registry.register(project, [AdapterCapability.GENERATES_PROJECT_FILES])
        registry.register(global_adapter, [AdapterCapability.GLOBAL_CONFIG_ONLY])

        project_adapters = registry.get_project_file_adapters()
        assert "project" in project_adapters
        assert "global" not in project_adapters

    def test_get_global_config_adapters(self):
        """Test getting global config adapters."""
        registry = AdapterRegistry()

        project = MockAdapter(name="project", description="Project adapter")
        global_adapter = MockAdapter(name="global", description="Global adapter")

        registry.register(project, [AdapterCapability.GENERATES_PROJECT_FILES])
        registry.register(global_adapter, [AdapterCapability.GLOBAL_CONFIG_ONLY])

        global_adapters = registry.get_global_config_adapters()
        assert "global" in global_adapters
        assert "project" not in global_adapters

    def test_discover_adapters(self):
        """Test discover_adapters method (currently a pass)."""
        registry = AdapterRegistry()
        # discover_adapters currently does nothing, just test it doesn't error
        registry.discover_adapters(Path("/fake/path"))
