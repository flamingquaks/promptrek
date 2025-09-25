"""
PrompTrek

A universal AI Editor prompt storage solution that allows developers to:
1. Create prompts/workflows in a universal, standardized format
2. Generate editor-specific prompts from the universal format using a CLI tool
3. Support multiple AI editors and tools with different prompt formats
"""

__version__ = "0.1.0"
__author__ = "PrompTrek Team"
__email__ = "team@promptrek.dev"

from .core.models import UniversalPrompt
from .core.parser import UPFParser
from .core.validator import UPFValidator

__all__ = [
    "UniversalPrompt",
    "UPFParser",
    "UPFValidator",
]
