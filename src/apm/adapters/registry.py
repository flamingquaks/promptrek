"""
Adapter registry for managing and discovering editor adapters.
"""

from typing import Dict, List, Type, Optional
import importlib
import pkgutil
from pathlib import Path

from .base import EditorAdapter
from ..core.exceptions import AdapterNotFoundError


class AdapterRegistry:
    """Registry for managing editor adapters."""
    
    def __init__(self):
        self._adapters: Dict[str, EditorAdapter] = {}
        self._adapter_classes: Dict[str, Type[EditorAdapter]] = {}
    
    def register(self, adapter: EditorAdapter) -> None:
        """Register an adapter instance."""
        self._adapters[adapter.name] = adapter
    
    def register_class(self, name: str, adapter_class: Type[EditorAdapter]) -> None:
        """Register an adapter class that will be instantiated on demand."""
        self._adapter_classes[name] = adapter_class
    
    def get(self, name: str) -> EditorAdapter:
        """Get an adapter by name."""
        if name in self._adapters:
            return self._adapters[name]
        
        if name in self._adapter_classes:
            # Instantiate the adapter class
            adapter_class = self._adapter_classes[name]
            adapter = adapter_class()
            self._adapters[name] = adapter
            return adapter
        
        raise AdapterNotFoundError(f"No adapter found for '{name}'")
    
    def list_adapters(self) -> List[str]:
        """Get list of all registered adapter names."""
        return list(set(self._adapters.keys()) | set(self._adapter_classes.keys()))
    
    def get_adapter_info(self, name: str) -> Dict[str, str]:
        """Get information about an adapter without instantiating it."""
        if name in self._adapters:
            adapter = self._adapters[name]
            return {
                'name': adapter.name,
                'description': adapter.description,
                'file_patterns': adapter.file_patterns,
                'status': 'available'
            }
        
        if name in self._adapter_classes:
            # Get class info without instantiating
            adapter_class = self._adapter_classes[name]
            return {
                'name': name,
                'description': getattr(adapter_class, '_description', 'No description'),
                'file_patterns': getattr(adapter_class, '_file_patterns', []),
                'status': 'available'
            }
        
        raise AdapterNotFoundError(f"No adapter found for '{name}'")
    
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