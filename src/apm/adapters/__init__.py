"""Editor adapters for Agent Prompt Mapper."""

from .base import EditorAdapter
from .claude import ClaudeAdapter
from .cline import ClineAdapter
from .codeium import CodeiumAdapter
from .continue_adapter import ContinueAdapter
from .copilot import CopilotAdapter
from .cursor import CursorAdapter
from .registry import AdapterRegistry, registry

# Register built-in adapters
registry.register_class("copilot", CopilotAdapter)
registry.register_class("cursor", CursorAdapter)
registry.register_class("continue", ContinueAdapter)
registry.register_class("claude", ClaudeAdapter)
registry.register_class("cline", ClineAdapter)
registry.register_class("codeium", CodeiumAdapter)

__all__ = [
    "EditorAdapter",
    "AdapterRegistry",
    "registry",
    "CopilotAdapter",
    "CursorAdapter",
    "ContinueAdapter",
    "ClaudeAdapter",
    "ClineAdapter",
    "CodeiumAdapter",
]
