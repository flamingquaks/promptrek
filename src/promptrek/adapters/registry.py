"""
Adapter registry for managing and discovering editor adapters.
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type

from ..core.exceptions import AdapterNotFoundError
from .base import EditorAdapter


class AdapterCapability(Enum):
    """Capabilities that an adapter can have."""

    GENERATES_PROJECT_FILES = "generates_project_files"
    GLOBAL_CONFIG_ONLY = "global_config_only"
    IDE_PLUGIN_ONLY = "ide_plugin_only"
    SUPPORTS_VARIABLES = "supports_variables"
    SUPPORTS_CONDITIONALS = "supports_conditionals"
    MULTIPLE_FILE_GENERATION = "multiple_file_generation"


class AdapterRegistry:
    """Registry for managing editor adapters."""

    def __init__(self) -> None:
        self._adapters: Dict[str, EditorAdapter] = {}
        self._adapter_classes: Dict[str, Type[EditorAdapter]] = {}
        self._capabilities: Dict[str, Set[AdapterCapability]] = {}

    def register(
        self,
        adapter: EditorAdapter,
        capabilities: Optional[List[AdapterCapability]] = None,
    ) -> None:
        """Register an adapter instance with its capabilities."""
        self._adapters[adapter.name] = adapter
        if capabilities:
            self._capabilities[adapter.name] = set(capabilities)

    def register_class(
        self,
        name: str,
        adapter_class: Type[EditorAdapter],
        capabilities: Optional[List[AdapterCapability]] = None,
    ) -> None:
        """Register an adapter class that will be instantiated on demand."""
        self._adapter_classes[name] = adapter_class
        if capabilities:
            self._capabilities[name] = set(capabilities)

    def get(self, name: str) -> EditorAdapter:
        """Get an adapter by name."""
        if name in self._adapters:
            return self._adapters[name]

        if name in self._adapter_classes:
            # Instantiate the adapter class
            adapter_class = self._adapter_classes[name]
            adapter = adapter_class()  # type: ignore[call-arg]
            self._adapters[name] = adapter
            return adapter

        raise AdapterNotFoundError(f"No adapter found for '{name}'")

    def list_adapters(self) -> List[str]:
        """Get list of all registered adapter names."""
        return list(set(self._adapters.keys()) | set(self._adapter_classes.keys()))

    def get_adapter_info(self, name: str) -> Dict[str, Any]:
        """Get information about an adapter without instantiating it."""
        if name in self._adapters:
            adapter = self._adapters[name]
            capabilities = self._capabilities.get(name, set())
            return {
                "name": adapter.name,
                "description": adapter.description,
                "file_patterns": adapter.file_patterns,
                "capabilities": [cap.value for cap in capabilities],
                "status": "available",
            }

        if name in self._adapter_classes:
            # Get class info without instantiating
            adapter_class = self._adapter_classes[name]
            capabilities = self._capabilities.get(name, set())
            return {
                "name": name,
                "description": getattr(adapter_class, "_description", "No description"),
                "file_patterns": getattr(adapter_class, "_file_patterns", []),
                "capabilities": [cap.value for cap in capabilities],
                "status": "available",
            }

        raise AdapterNotFoundError(f"No adapter found for '{name}'")

    def get_adapters_by_capability(self, capability: AdapterCapability) -> List[str]:
        """Get list of adapter names that have a specific capability."""
        return [name for name, caps in self._capabilities.items() if capability in caps]

    def has_capability(self, adapter_name: str, capability: AdapterCapability) -> bool:
        """Check if an adapter has a specific capability."""
        return capability in self._capabilities.get(adapter_name, set())

    def get_project_file_adapters(self) -> List[str]:
        """Get adapters that generate project-level configuration files."""
        return self.get_adapters_by_capability(
            AdapterCapability.GENERATES_PROJECT_FILES
        )

    def get_global_config_adapters(self) -> List[str]:
        """Get adapters that only support global configuration."""
        return self.get_adapters_by_capability(AdapterCapability.GLOBAL_CONFIG_ONLY)

    def discover_adapters(self, package_path: Path) -> None:
        """
        Discover and register adapters from a package directory.

        Args:
            package_path: Path to the adapters package
        """
        # This would scan for adapter modules and register them automatically
        # For now, we'll implement manual registration
        pass


# Global adapter registry instance
registry = AdapterRegistry()
