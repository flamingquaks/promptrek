"""
Base adapter class and interface definitions for editor adapters.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..core.models import UniversalPrompt
from ..core.exceptions import ValidationError


class EditorAdapter(ABC):
    """Base class for all editor adapters."""
    
    def __init__(self, name: str, description: str, file_patterns: List[str]):
        """
        Initialize the adapter.
        
        Args:
            name: The editor name (e.g., 'copilot', 'cursor')
            description: Human-readable description
            file_patterns: List of file patterns this adapter generates
        """
        self.name = name
        self.description = description
        self.file_patterns = file_patterns
    
    @abstractmethod
    def generate(self, prompt: UniversalPrompt, output_dir: Path, dry_run: bool = False, verbose: bool = False) -> List[Path]:
        """
        Generate editor-specific files from a universal prompt.
        
        Args:
            prompt: The parsed universal prompt
            output_dir: Directory to generate files in
            dry_run: If True, don't create files, just show what would be created
            verbose: Enable verbose output
            
        Returns:
            List of file paths that were created (or would be created in dry run)
        """
        pass
    
    @abstractmethod
    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """
        Validate a prompt for this specific editor.
        
        Args:
            prompt: The universal prompt to validate
            
        Returns:
            List of validation errors specific to this editor
        """
        pass
    
    def supports_variables(self) -> bool:
        """Return True if this adapter supports variable substitution."""
        return False
    
    def supports_conditionals(self) -> bool:
        """Return True if this adapter supports conditional instructions."""
        return False
    
    def get_required_variables(self, prompt: UniversalPrompt) -> List[str]:
        """
        Get list of variables required by this adapter for the given prompt.
        
        Args:
            prompt: The universal prompt
            
        Returns:
            List of variable names required
        """
        return []