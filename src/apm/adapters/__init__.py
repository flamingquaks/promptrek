"""Editor adapters for Agent Prompt Mapper."""

from .amazon_q import AmazonQAdapter
from .base import EditorAdapter
from .claude import ClaudeAdapter
from .cline import ClineAdapter
from .codeium import CodeiumAdapter
from .continue_adapter import ContinueAdapter
from .copilot import CopilotAdapter
from .cursor import CursorAdapter
from .jetbrains import JetBrainsAdapter
from .kiro import KiroAdapter
from .registry import AdapterRegistry, registry
from .tabnine import TabnineAdapter

# Register built-in adapters
registry.register_class("copilot", CopilotAdapter)
registry.register_class("cursor", CursorAdapter)
registry.register_class("continue", ContinueAdapter)
registry.register_class("claude", ClaudeAdapter)
registry.register_class("cline", ClineAdapter)
registry.register_class("codeium", CodeiumAdapter)
registry.register_class("kiro", KiroAdapter)
registry.register_class("tabnine", TabnineAdapter)
registry.register_class("amazon-q", AmazonQAdapter)
registry.register_class("jetbrains", JetBrainsAdapter)

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
    "KiroAdapter",
    "TabnineAdapter",
    "AmazonQAdapter",
    "JetBrainsAdapter",
]
