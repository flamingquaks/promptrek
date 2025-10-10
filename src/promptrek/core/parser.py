"""
Universal Prompt Format (UPF) parser.

Handles loading and parsing .promptrek.yaml files into UniversalPrompt objects.
"""

from pathlib import Path
from typing import Any, Dict, List, Sequence, Union

import yaml
from pydantic import ValidationError

from .exceptions import UPFFileNotFoundError, UPFParsingError
from .models import UniversalPrompt, UniversalPromptV2


class UPFParser:
    """Parser for Universal Prompt Format files."""

    def __init__(self) -> None:
        """Initialize the UPF parser."""
        pass

    def parse_file(
        self, file_path: Union[str, Path]
    ) -> Union[UniversalPrompt, UniversalPromptV2]:
        """
        Parse a UPF file from disk.

        Args:
            file_path: Path to the .promptrek.yaml file

        Returns:
            Parsed UniversalPrompt (v1) or UniversalPromptV2 (v2) object

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

        # Process imports if present (v1 only)
        if isinstance(prompt, UniversalPrompt) and prompt.imports:
            from ..utils import ImportProcessor

            import_processor = ImportProcessor()
            prompt = import_processor.process_imports(prompt, file_path.parent)

        return prompt

    def parse_dict(
        self, data: Dict[str, Any], source: str = "<dict>"
    ) -> Union[UniversalPrompt, UniversalPromptV2]:
        """
        Parse a UPF dictionary into a UniversalPrompt object.

        Automatically detects schema version and uses appropriate model.

        Args:
            data: Dictionary containing UPF data
            source: Source identifier for error messages

        Returns:
            Parsed UniversalPrompt (v1) or UniversalPromptV2 (v2) object

        Raises:
            UPFParsingError: If parsing or validation fails
        """
        if not isinstance(data, dict):
            raise UPFParsingError(
                f"UPF data must be a dictionary, got {type(data)} in {source}"
            )

        # Detect version from schema_version field
        schema_version = data.get("schema_version", "1.0.0")
        major_version = self._get_major_version(schema_version)

        try:
            if major_version == "2":
                # Use v2 model
                return UniversalPromptV2(**data)
            else:
                # Use v1 model (default for backwards compatibility)
                return UniversalPrompt(**data)
        except ValidationError as e:
            error_msg = self._format_validation_error(e, source)
            raise UPFParsingError(error_msg)
        except Exception as e:
            raise UPFParsingError(f"Unexpected error parsing {source}: {e}")

    def _get_major_version(self, version_str: str) -> str:
        """Extract major version from version string."""
        try:
            return version_str.split(".")[0]
        except (AttributeError, IndexError):
            return "1"  # Default to v1 if invalid format

    def parse_string(
        self, yaml_content: str, source: str = "<string>"
    ) -> Union[UniversalPrompt, UniversalPromptV2]:
        """
        Parse a UPF YAML string into a UniversalPrompt object.

        Args:
            yaml_content: YAML content as string
            source: Source identifier for error messages

        Returns:
            Parsed UniversalPrompt (v1) or UniversalPromptV2 (v2) object

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
    ) -> List[Path]:
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

    def parse_multiple_files(
        self, file_paths: Sequence[Union[str, Path]]
    ) -> Union[UniversalPrompt, UniversalPromptV2]:
        """
        Parse multiple UPF files and merge them into a single UniversalPrompt.

        Args:
            file_paths: List of paths to .promptrek.yaml files

        Returns:
            Merged UniversalPrompt object

        Raises:
            UPFParsingError: If parsing fails
        """
        if not file_paths:
            raise UPFParsingError("No files provided for parsing")

        # Parse the first file as the base
        base_prompt = self.parse_file(file_paths[0])

        # Merge additional files
        for file_path in file_paths[1:]:
            additional_prompt = self.parse_file(file_path)
            base_prompt = self._merge_prompts(base_prompt, additional_prompt)

        return base_prompt

    def parse_directory(
        self, directory: Union[str, Path], recursive: bool = True
    ) -> Union[UniversalPrompt, UniversalPromptV2]:
        """
        Find and parse all UPF files in a directory, merging them into one.

        Args:
            directory: Directory to search for .promptrek.yaml files
            recursive: Whether to search recursively

        Returns:
            Merged UniversalPrompt object

        Raises:
            UPFParsingError: If no files found or parsing fails
        """
        upf_files = self.find_upf_files(directory, recursive)

        if not upf_files:
            raise UPFParsingError(f"No .promptrek.yaml files found in {directory}")

        # Sort files for consistent merging order
        upf_files.sort()

        return self.parse_multiple_files(upf_files)

    def _merge_prompts(
        self,
        base: Union[UniversalPrompt, UniversalPromptV2],
        additional: Union[UniversalPrompt, UniversalPromptV2],
    ) -> Union[UniversalPrompt, UniversalPromptV2]:
        """
        Merge two UniversalPrompt objects, with additional taking precedence.

        Args:
            base: Base prompt to merge into
            additional: Additional prompt to merge from

        Returns:
            Merged UniversalPrompt object
        """
        # V2 merging: simple content concatenation
        if isinstance(base, UniversalPromptV2) or isinstance(
            additional, UniversalPromptV2
        ):
            # For v2, we can't meaningfully merge - just return the additional
            # This is a limitation of the simplified v2 format
            return additional

        # Convert to dicts for easier merging (v1 only)
        base_dict = base.model_dump()
        additional_dict = additional.model_dump()

        # Merge metadata - additional takes precedence for most fields
        if additional_dict.get("metadata"):
            if "metadata" not in base_dict:
                base_dict["metadata"] = {}
            base_dict["metadata"].update(additional_dict["metadata"])

        # Merge context - combine lists, additional takes precedence for simple fields
        if additional_dict.get("context"):
            if "context" not in base_dict:
                base_dict["context"] = {}

            context = base_dict["context"]
            add_context = additional_dict["context"]

            # Simple fields - additional takes precedence
            for field in ["project_type", "description"]:
                if add_context.get(field):
                    context[field] = add_context[field]

            # List fields - combine and deduplicate
            if add_context.get("technologies"):
                existing = context.get("technologies", [])
                combined = existing + add_context["technologies"]
                context["technologies"] = list(
                    dict.fromkeys(combined)
                )  # Remove duplicates

        # Merge instructions - combine lists
        if additional_dict.get("instructions"):
            if "instructions" not in base_dict:
                base_dict["instructions"] = {}

            instructions = base_dict["instructions"]
            add_instructions = additional_dict["instructions"]

            for inst_type in ["general", "code_style", "testing"]:
                if add_instructions.get(inst_type):
                    existing = instructions.get(inst_type, []) or []
                    instructions[inst_type] = existing + add_instructions[inst_type]

        # Merge examples - additional takes precedence for conflicts
        if additional_dict.get("examples"):
            if "examples" not in base_dict:
                base_dict["examples"] = {}
            base_dict["examples"].update(additional_dict["examples"])

        # Merge variables - additional takes precedence for conflicts
        if additional_dict.get("variables"):
            if "variables" not in base_dict:
                base_dict["variables"] = {}
            base_dict["variables"].update(additional_dict["variables"])

        # Merge conditions - combine lists
        if additional_dict.get("conditions"):
            existing_conditions = base_dict.get("conditions", []) or []
            base_dict["conditions"] = (
                existing_conditions + additional_dict["conditions"]
            )

        # Merge targets - combine and deduplicate
        if additional_dict.get("targets"):
            existing_targets = base_dict.get("targets", []) or []
            combined_targets = existing_targets + additional_dict["targets"]
            base_dict["targets"] = list(dict.fromkeys(combined_targets))

        # Merge editor_specific - additional takes precedence for conflicts
        if additional_dict.get("editor_specific"):
            if "editor_specific" not in base_dict:
                base_dict["editor_specific"] = {}
            base_dict["editor_specific"].update(additional_dict["editor_specific"])

        # Merge imports - combine lists
        if additional_dict.get("imports"):
            existing_imports = base_dict.get("imports", []) or []
            base_dict["imports"] = existing_imports + additional_dict["imports"]

        # Create new merged prompt
        return UniversalPrompt(**base_dict)
