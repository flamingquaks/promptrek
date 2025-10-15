"""
Import processing utilities for PromptTrek.

Handles importing and merging content from other UPF files.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from ..core.exceptions import UPFParsingError
from ..core.models import ImportConfig, UniversalPrompt, UniversalPromptV2
from ..core.parser import UPFParser


class ImportProcessor:
    """Processes import declarations in UPF prompts."""

    def __init__(self) -> None:
        """Initialize import processor."""
        self.parser = UPFParser()
        self._processed_files: set[Path] = set()  # Prevent circular imports

    def process_imports(
        self, prompt: UniversalPrompt, base_path: Path
    ) -> UniversalPrompt:
        """
        Process all import declarations in a prompt.

        Args:
            prompt: The universal prompt with imports
            base_path: Base path for resolving relative imports

        Returns:
            Prompt with imported content merged
        """
        if not prompt.imports:
            return prompt

        # Start with current prompt data
        merged_data = prompt.model_dump(by_alias=True)

        # Process each import
        for import_config in prompt.imports:
            imported_data = self._process_single_import(import_config, base_path)
            merged_data = self._merge_imported_data(
                merged_data, imported_data, import_config.prefix
            )

        # Remove imports from final data to avoid recursion
        merged_data.pop("imports", None)

        return UniversalPrompt.model_validate(merged_data)

    def _process_single_import(
        self, import_config: ImportConfig, base_path: Path
    ) -> Dict[str, Any]:
        """
        Process a single import configuration.

        Args:
            import_config: Import configuration
            base_path: Base path for resolving relative paths

        Returns:
            Dictionary containing imported data
        """
        import_path = base_path / import_config.path

        # Prevent circular imports
        abs_path = import_path.resolve()
        if abs_path in self._processed_files:
            raise UPFParsingError(f"Circular import detected: {import_path}")

        self._processed_files.add(abs_path)

        try:
            imported_prompt = self.parser.parse_file(import_path)

            # V2 prompts don't support imports
            if isinstance(imported_prompt, UniversalPromptV2):
                raise UPFParsingError(f"Cannot import v2 format file: {import_path}")

            # Recursively process imports in the imported file
            if imported_prompt.imports:
                imported_prompt = self.process_imports(
                    imported_prompt, import_path.parent
                )

            return imported_prompt.model_dump(by_alias=True)
        except Exception as e:
            raise UPFParsingError(f"Failed to import {import_path}: {e}")
        finally:
            self._processed_files.discard(abs_path)

    def _merge_imported_data(
        self,
        base_data: Dict[str, Any],
        imported_data: Dict[str, Any],
        prefix: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Merge imported data into base data.

        Args:
            base_data: Base prompt data
            imported_data: Data from imported file
            prefix: Optional prefix for namespacing

        Returns:
            Merged data dictionary
        """
        # Don't merge metadata and schema info
        skip_fields = {"schema_version", "metadata", "targets"}

        for key, value in imported_data.items():
            if key in skip_fields:
                continue

            if key == "instructions" and isinstance(value, dict):
                self._merge_instructions(base_data, value, prefix)
            elif key == "examples" and isinstance(value, dict):
                self._merge_examples(base_data, value, prefix)
            elif key == "variables" and isinstance(value, dict):
                self._merge_variables(base_data, value, prefix)
            elif key not in base_data:
                # Add new fields directly
                base_data[key] = value

        return base_data

    def _merge_instructions(
        self,
        base_data: Dict[str, Any],
        imported_instructions: Dict[str, Any],
        prefix: Optional[str],
    ) -> None:
        """Merge instructions from imported file."""
        if "instructions" not in base_data:
            base_data["instructions"] = {}

        base_instructions = base_data["instructions"]

        for category, instructions in imported_instructions.items():
            if isinstance(instructions, list):
                if category not in base_instructions:
                    base_instructions[category] = []
                elif base_instructions[category] is None:
                    base_instructions[category] = []

                # Add prefix to instruction text if specified
                for instruction in instructions:
                    prefixed_instruction = (
                        f"[{prefix}] {instruction}" if prefix else instruction
                    )
                    base_instructions[category].append(prefixed_instruction)

    def _merge_examples(
        self,
        base_data: Dict[str, Any],
        imported_examples: Dict[str, Any],
        prefix: Optional[str],
    ) -> None:
        """Merge examples from imported file."""
        if "examples" not in base_data or base_data["examples"] is None:
            base_data["examples"] = {}

        base_examples = base_data["examples"]

        for name, example in imported_examples.items():
            # Add prefix to example name if specified
            prefixed_name = f"{prefix}_{name}" if prefix else name
            base_examples[prefixed_name] = example

    def _merge_variables(
        self,
        base_data: Dict[str, Any],
        imported_variables: Dict[str, Any],
        prefix: Optional[str],
    ) -> None:
        """Merge variables from imported file."""
        if "variables" not in base_data or base_data["variables"] is None:
            base_data["variables"] = {}

        base_variables = base_data["variables"]

        for name, value in imported_variables.items():
            # Add prefix to variable name if specified and not already present in base
            prefixed_name = f"{prefix}_{name}" if prefix else name
            if prefixed_name not in base_variables:
                base_variables[prefixed_name] = value
