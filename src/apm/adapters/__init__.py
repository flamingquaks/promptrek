"""Editor adapters for Agent Prompt Mapper."""

from .base import EditorAdapter
from .registry import AdapterRegistry, registry
from .copilot import CopilotAdapter
from .cursor import CursorAdapter
from .continue_adapter import ContinueAdapter

# Register built-in adapters
registry.register_class("copilot", CopilotAdapter)
registry.register_class("cursor", CursorAdapter)
registry.register_class("continue", ContinueAdapter)

__all__ = [
    "EditorAdapter",
    "AdapterRegistry", 
    "registry",
    "CopilotAdapter",
    "CursorAdapter", 
    "ContinueAdapter"
]