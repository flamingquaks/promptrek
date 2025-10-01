"""
PrompTrek

A universal AI Editor prompt storage solution that allows developers to:
1. Create prompts/workflows in a universal, standardized format
2. Generate editor-specific prompts from the universal format using a CLI tool
3. Support multiple AI editors and tools with different prompt formats
"""

import importlib.metadata

__version__ = importlib.metadata.version("promptrek")

from .core.models import UniversalPrompt
from .core.parser import UPFParser
from .core.validator import UPFValidator

__all__ = [
    "UniversalPrompt",
    "UPFParser",
    "UPFValidator",
]
