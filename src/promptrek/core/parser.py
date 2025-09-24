"""
Universal Prompt Format (UPF) parser.

Handles loading and parsing .promptrek.yaml files into UniversalPrompt objects.
"""

from pathlib import Path
from typing import Any, Dict, Union

import yaml
from pydantic import ValidationError

from .exceptions import UPFFileNotFoundError, UPFParsingError
from .models import UniversalPrompt


class UPFParser:
    """Parser for Universal Prompt Format files."""

    def __init__(self) -> None:
        """Initialize the UPF parser."""
        pass

    def parse_file(self, file_path: Union[str, Path]) -> UniversalPrompt:
        """
        Parse a UPF file from disk.

        Args:
            file_path: Path to the .promptrek.yaml file

        Returns:
            Parsed UniversalPrompt object

        Raises:
            UPFFileNotFoundError: If the file doesn't exist
            UPFParsingError: If parsing fails
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise UPFFileNotFoundError(f"UPF file not found: {file_path}")

        if file_path.suffix not in [".yaml", ".yml"]:
            raise UPFParsingError(
                f"File must have .yaml or .yml extension: {file_path}"
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise UPFParsingError(f"YAML parsing error in {file_path}: {e}")
        except Exception as e:
            raise UPFParsingError(f"Error reading file {file_path}: {e}")

        prompt = self.parse_dict(data, str(file_path))

        # Process imports if present
        if prompt.imports:
            from ..utils import ImportProcessor

            import_processor = ImportProcessor()
            prompt = import_processor.process_imports(prompt, file_path.parent)

        return prompt

    def parse_dict(
        self, data: Dict[str, Any], source: str = "<dict>"
    ) -> UniversalPrompt:
        """
        Parse a UPF dictionary into a UniversalPrompt object.

        Args:
            data: Dictionary containing UPF data
            source: Source identifier for error messages

        Returns:
            Parsed UniversalPrompt object

        Raises:
            UPFParsingError: If parsing or validation fails
        """
        if not isinstance(data, dict):
            raise UPFParsingError(
                f"UPF data must be a dictionary, got {type(data)} in {source}"
            )

        try:
            return UniversalPrompt(**data)
        except ValidationError as e:
            error_msg = self._format_validation_error(e, source)
            raise UPFParsingError(error_msg)
        except Exception as e:
            raise UPFParsingError(f"Unexpected error parsing {source}: {e}")

    def parse_string(
        self, yaml_content: str, source: str = "<string>"
    ) -> UniversalPrompt:
        """
        Parse a UPF YAML string into a UniversalPrompt object.

        Args:
            yaml_content: YAML content as string
            source: Source identifier for error messages

        Returns:
            Parsed UniversalPrompt object

        Raises:
            UPFParsingError: If parsing fails
        """
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise UPFParsingError(f"YAML parsing error in {source}: {e}")

        return self.parse_dict(data, source)

    def validate_file_extension(self, file_path: Union[str, Path]) -> bool:
        """
        Check if file has a valid UPF extension.

        Args:
            file_path: Path to check

        Returns:
            True if extension is valid (.promptrek.yaml or .promptrek.yml)
        """
        file_path = Path(file_path)
        name = file_path.name
        return name.endswith(".promptrek.yaml") or name.endswith(".promptrek.yml")

    def find_upf_files(
        self, directory: Union[str, Path], recursive: bool = False
    ) -> list[Path]:
        """
        Find all UPF files in a directory.

        Args:
            directory: Directory to search
            recursive: Whether to search recursively

        Returns:
            List of paths to UPF files
        """
        directory = Path(directory)

        if not directory.exists() or not directory.is_dir():
            return []

        pattern = "**/*.promptrek.y*ml" if recursive else "*.promptrek.y*ml"
        return list(directory.glob(pattern))

    def _format_validation_error(self, error: ValidationError, source: str) -> str:
        """
        Format a Pydantic validation error into a readable message.

        Args:
            error: The validation error
            source: Source identifier

        Returns:
            Formatted error message
        """
        messages = []
        for err in error.errors():
            field = " -> ".join(str(loc) for loc in err["loc"])
            msg = err["msg"]
            messages.append(f"  {field}: {msg}")

        return f"Validation errors in {source}:\n" + "\n".join(messages)
