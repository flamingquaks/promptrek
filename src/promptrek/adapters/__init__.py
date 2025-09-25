"""Editor adapters for PromptTrek."""

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
from .registry import AdapterCapability, AdapterRegistry, registry
from .tabnine import TabnineAdapter

# Register built-in adapters with their capabilities

# Tools that generate project-level configuration files
registry.register_class(
    "copilot",
    CopilotAdapter,
    [
        AdapterCapability.GENERATES_PROJECT_FILES,
        AdapterCapability.SUPPORTS_VARIABLES,
        AdapterCapability.SUPPORTS_CONDITIONALS,
    ],
)

registry.register_class(
    "cursor",
    CursorAdapter,
    [
        AdapterCapability.GENERATES_PROJECT_FILES,
        AdapterCapability.SUPPORTS_VARIABLES,
        AdapterCapability.SUPPORTS_CONDITIONALS,
    ],
)

registry.register_class(
    "continue",
    ContinueAdapter,
    [
        AdapterCapability.GENERATES_PROJECT_FILES,
        AdapterCapability.SUPPORTS_VARIABLES,
        AdapterCapability.SUPPORTS_CONDITIONALS,
    ],
)

registry.register_class(
    "claude",
    ClaudeAdapter,
    [
        AdapterCapability.GENERATES_PROJECT_FILES,
        AdapterCapability.SUPPORTS_VARIABLES,
        AdapterCapability.SUPPORTS_CONDITIONALS,
    ],
)

registry.register_class(
    "cline",
    ClineAdapter,
    [
        AdapterCapability.GENERATES_PROJECT_FILES,
        AdapterCapability.SUPPORTS_VARIABLES,
        AdapterCapability.SUPPORTS_CONDITIONALS,
    ],
)

registry.register_class(
    "kiro",
    KiroAdapter,
    [
        AdapterCapability.GENERATES_PROJECT_FILES,
        AdapterCapability.SUPPORTS_VARIABLES,
        AdapterCapability.SUPPORTS_CONDITIONALS,
    ],
)

# Tools that only support global configuration (don't generate project files)
registry.register_class(
    "amazon-q", AmazonQAdapter, [AdapterCapability.GLOBAL_CONFIG_ONLY]
)

registry.register_class(
    "jetbrains", JetBrainsAdapter, [AdapterCapability.IDE_PLUGIN_ONLY]
)

registry.register_class(
    "tabnine", TabnineAdapter, [AdapterCapability.GLOBAL_CONFIG_ONLY]
)

# Windsurf (replaces Codeium) - IDE-based configuration only
registry.register_class("windsurf", CodeiumAdapter, [AdapterCapability.IDE_PLUGIN_ONLY])

__all__ = [
    "EditorAdapter",
    "AdapterRegistry",
    "AdapterCapability",
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
