"""
Base adapter class and interface definitions for editor adapters.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.exceptions import ValidationError
from ..core.models import UniversalPrompt, UniversalPromptV2, UniversalPromptV3
from ..utils import ConditionalProcessor, VariableSubstitution


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
        self._variable_substitution = VariableSubstitution()
        self._conditional_processor = ConditionalProcessor()

    @abstractmethod
    def generate(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> List[Path]:
        """
        Generate editor-specific files from a universal prompt.

        Args:
            prompt: The parsed universal prompt (v1, v2, or v3)
            output_dir: Directory to generate files in
            dry_run: If True, don't create files, just show what would be created
            verbose: Enable verbose output
            variables: Additional variables for substitution
            headless: Generate with headless agent instructions

        Returns:
            List of file paths that were created (or would be created in dry run)
        """
        pass

    @abstractmethod
    def validate(
        self, prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]
    ) -> List[ValidationError]:
        """
        Validate a prompt for this specific editor.

        Args:
            prompt: The universal prompt to validate (v1, v2, or v3)

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

    def supports_hooks(self) -> bool:
        """Return True if this adapter supports hooks system."""
        return False

    def supports_bidirectional_sync(self) -> bool:
        """Return True if this adapter supports parsing files back to UniversalPrompt."""
        try:
            # Check if parse_files exists and is callable
            parse_method = getattr(self, "parse_files", None)
            return parse_method is not None and callable(parse_method)
        except AttributeError:
            return False

    def parse_files(
        self, source_dir: Path
    ) -> Union["UniversalPrompt", "UniversalPromptV2", "UniversalPromptV3"]:
        """
        Parse editor-specific files back into a UniversalPrompt, UniversalPromptV2, or UniversalPromptV3.

        Args:
            source_dir: Directory containing editor-specific files

        Returns:
            UniversalPrompt, UniversalPromptV2, or UniversalPromptV3 object parsed from editor files

        Raises:
            NotImplementedError: If adapter doesn't support reverse parsing
        """
        raise NotImplementedError(
            f"{self.name} adapter does not support bidirectional sync"
        )

    def get_required_variables(self, prompt: UniversalPrompt) -> List[str]:
        """
        Get list of variables required by this adapter for the given prompt.

        Args:
            prompt: The universal prompt

        Returns:
            List of variable names required
        """
        return []

    def substitute_variables(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        variables: Optional[Dict[str, Any]] = None,
    ) -> Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]:
        """
        Apply variable substitution to a prompt if this adapter supports it.

        Args:
            prompt: The universal prompt (v1, v2, or v3)
            variables: Additional variables to substitute

        Returns:
            Prompt with variables substituted (or original if not supported)
        """
        if not self.supports_variables():
            return prompt

        # V2/V3 prompts don't need structured variable substitution
        # (it's done directly on content in the adapter)
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            return prompt

        return self._variable_substitution.substitute_prompt(
            prompt, variables, env_variables=True, strict=False
        )

    def process_conditionals(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        variables: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process conditional instructions if this adapter supports them.

        Args:
            prompt: The universal prompt (v1, v2, or v3)
            variables: Variables for condition evaluation

        Returns:
            Additional content from conditional processing
        """
        if not self.supports_conditionals():
            return {}

        # V2/V3 prompts don't have conditions field
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            return {}

        # Add editor name to variables for condition evaluation
        eval_variables = variables.copy() if variables else {}
        eval_variables["EDITOR"] = self.name

        return self._conditional_processor.process_conditions(prompt, eval_variables)

    def generate_multiple(
        self,
        prompt_files: List[
            Tuple[Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3], Path]
        ],
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> List[Path]:
        """
        Generate separate files for each prompt (optional method).

        This method is used by adapters that support generating separate files
        for each input prompt file.

        Args:
            prompt_files: List of (UniversalPrompt, UniversalPromptV2, or UniversalPromptV3, Path) tuples
            output_dir: Directory to generate files in
            dry_run: If True, don't create files, just show what would be created
            verbose: Enable verbose output
            variables: Additional variables for substitution
            headless: Generate with headless agent instructions

        Returns:
            List of paths to generated files (empty if not supported)

        Raises:
            NotImplementedError: If adapter doesn't support multiple file generation
        """
        raise NotImplementedError(
            f"{self.name} adapter does not support multiple file generation"
        )

    def generate_merged(
        self,
        prompt_files: List[
            Tuple[Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3], Path]
        ],
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> List[Path]:
        """
        Generate merged files from multiple prompts (optional method).

        This method is used by adapters that support merging multiple prompt
        files into a single configuration.

        Args:
            prompt_files: List of (UniversalPrompt, UniversalPromptV2, or UniversalPromptV3, Path) tuples
            output_dir: Directory to generate files in
            dry_run: If True, don't create files, just show what would be created
            verbose: Enable verbose output
            variables: Additional variables for substitution
            headless: Generate with headless agent instructions

        Returns:
            List of paths to generated files (empty if not supported)

        Raises:
            NotImplementedError: If adapter doesn't support merged file generation
        """
        raise NotImplementedError(
            f"{self.name} adapter does not support merged file generation"
        )
