"""
Mixin class for bidirectional sync support in adapters.

Provides common functionality for parsing markdown-based configuration files
back into UniversalPrompt format.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import click
import yaml

from ..core.models import (
    DocumentConfig,
    Instructions,
    ProjectContext,
    PromptMetadata,
    UniversalPrompt,
    UniversalPromptV2,
)


class MarkdownSyncMixin:
    """
    Mixin class that provides markdown file parsing for sync functionality.

    Adapters that use markdown-based rules files can inherit from this mixin
    to get automatic sync support.
    """

    def parse_markdown_rules_files(
        self,
        source_dir: Path,
        rules_subdir: str,
        file_extension: str = "md",
        editor_name: str = "AI Assistant",
    ) -> UniversalPrompt:
        """
        Parse markdown rules files back into a UniversalPrompt.

        Args:
            source_dir: Root directory containing editor configuration
            rules_subdir: Subdirectory path relative to source_dir (e.g., ".cursor/rules")
            file_extension: File extension to look for (e.g., "md", "mdc")
            editor_name: Name of the editor for metadata

        Returns:
            UniversalPrompt object parsed from markdown files
        """
        # Initialize parsed data
        metadata = PromptMetadata(
            title=f"{editor_name} Configuration",
            description=f"Configuration parsed from {editor_name} files",
            version="1.0.0",
            author="PrompTrek Sync",
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
            tags=[editor_name.lower().replace(" ", "-"), "synced"],
        )

        instructions = Instructions()
        technologies = []

        # Parse markdown files from rules directory
        rules_dir = source_dir / rules_subdir
        if rules_dir.exists():
            instructions_dict: Dict[str, List[str]] = {}

            pattern = f"*.{file_extension}"
            for md_file in rules_dir.glob(pattern):
                try:
                    instructions_from_file = self._parse_markdown_file(md_file)

                    # Map file names to instruction categories
                    filename = md_file.stem
                    category = self._map_filename_to_category(filename)

                    if category == "technology":
                        # Extract technology name from filename
                        tech = self._extract_technology_from_filename(filename)
                        if tech:
                            technologies.append(tech)
                        # Add to general instructions
                        if "general" not in instructions_dict:
                            instructions_dict["general"] = []
                        instructions_dict["general"].extend(instructions_from_file)
                    elif category:
                        if category not in instructions_dict:
                            instructions_dict[category] = []
                        instructions_dict[category].extend(instructions_from_file)

                except Exception as e:
                    click.echo(f"Warning: Could not parse {md_file}: {e}")

            # Update instructions object
            for category, instrs in instructions_dict.items():
                if instrs:
                    # Deduplicate instructions
                    unique_instrs = list(dict.fromkeys(instrs))
                    setattr(instructions, category, unique_instrs)

        # Create context if technologies were found
        context = None
        if technologies:
            context = ProjectContext(
                project_type="application",
                technologies=list(set(technologies)),  # Deduplicate
                description=f"Project using {', '.join(set(technologies))}",
            )

        # Determine target based on editor name
        target = editor_name.lower().replace(" ", "-")

        return UniversalPrompt(
            schema_version="1.0.0",
            metadata=metadata,
            targets=[target],
            context=context,
            instructions=instructions,
        )

    def _parse_markdown_file(self, md_file: Path) -> List[str]:
        """
        Parse markdown file and extract bullet point instructions.

        Args:
            md_file: Path to markdown file

        Returns:
            List of instruction strings
        """
        instructions = []

        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse frontmatter if exists (skip it)
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    content = parts[2]

            # Extract bullet points (lines starting with - or *)
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("- ") or line.startswith("* "):
                    instruction = line[2:].strip()
                    # Skip empty lines and headings
                    if instruction and not instruction.startswith("#"):
                        instructions.append(instruction)

        except Exception as e:
            click.echo(f"Error parsing {md_file}: {e}")

        return instructions

    def _map_filename_to_category(self, filename: str) -> Optional[str]:
        """
        Map a filename to an instruction category.

        Args:
            filename: Filename without extension

        Returns:
            Category name or None
        """
        filename_lower = filename.lower()

        # Direct mappings
        if filename_lower in ["general", "index", "context", "project"]:
            return "general"
        elif "code-style" in filename_lower or "coding-standards" in filename_lower:
            return "code_style"
        elif "test" in filename_lower:
            return "testing"
        elif "security" in filename_lower:
            return "security"
        elif "performance" in filename_lower:
            return "performance"
        elif "architecture" in filename_lower:
            return "architecture"
        elif filename_lower.endswith("-rules") or filename_lower.endswith(
            "-guidelines"
        ):
            return "technology"
        else:
            # Default to general if unknown
            return "general"

    def _extract_technology_from_filename(self, filename: str) -> Optional[str]:
        """
        Extract technology name from filename.

        Args:
            filename: Filename without extension

        Returns:
            Technology name or None
        """
        filename_lower = filename.lower()

        # Remove common suffixes
        for suffix in ["-rules", "-guidelines", "-guide"]:
            if filename_lower.endswith(suffix):
                return filename_lower.replace(suffix, "")

        return None


class SingleFileMarkdownSyncMixin:
    """
    Mixin for adapters that use a single markdown file (like Claude Code).
    """

    def parse_single_markdown_file(
        self,
        source_dir: Path,
        file_path: str,
        editor_name: str = "AI Assistant",
    ) -> UniversalPrompt:
        """
        Parse a single markdown file back into a UniversalPrompt (v1 - legacy).

        Args:
            source_dir: Root directory containing editor configuration
            file_path: Path to the file relative to source_dir (e.g., ".claude/CLAUDE.md")
            editor_name: Name of the editor for metadata

        Returns:
            UniversalPrompt object parsed from the markdown file
        """
        # Initialize parsed data
        metadata = PromptMetadata(
            title=f"{editor_name} Configuration",
            description=f"Configuration parsed from {editor_name} file",
            version="1.0.0",
            author="PrompTrek Sync",
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
            tags=[editor_name.lower().replace(" ", "-"), "synced"],
        )

        instructions = Instructions()
        context = None

        # Parse the single markdown file
        md_file = source_dir / file_path
        if md_file.exists():
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse sections
                instructions_dict = self._parse_markdown_sections(content)

                # Update instructions object
                for category, instrs in instructions_dict.items():
                    if instrs:
                        setattr(instructions, category, instrs)

                # Try to extract project context from content
                context = self._extract_context_from_content(content)

            except Exception as e:
                click.echo(f"Warning: Could not parse {md_file}: {e}")

        target = editor_name.lower().replace(" ", "-")

        return UniversalPrompt(
            schema_version="1.0.0",
            metadata=metadata,
            targets=[target],
            context=context,
            instructions=instructions,
        )

    def parse_single_markdown_file_v2(
        self,
        source_dir: Path,
        file_path: str,
        editor_name: str = "AI Assistant",
    ) -> UniversalPromptV2:
        """
        Parse a single markdown file into UniversalPromptV2 (lossless).

        This method preserves the markdown content exactly as-is, extracting
        only minimal metadata. Perfect for lossless bidirectional sync.

        Args:
            source_dir: Root directory containing editor configuration
            file_path: Path to the file relative to source_dir
            editor_name: Name of the editor for metadata

        Returns:
            UniversalPromptV2 object with lossless markdown content
        """
        md_file = source_dir / file_path

        if not md_file.exists():
            raise FileNotFoundError(f"File not found: {md_file}")

        # Read the file
        with open(md_file, "r", encoding="utf-8") as f:
            full_content = f.read()

        # Extract frontmatter if present
        frontmatter_data, content = self._extract_frontmatter(full_content)

        # Extract title from first H1 or use default
        title = (
            self._extract_title_from_markdown(content) or f"{editor_name} Configuration"
        )

        # Create metadata
        metadata = PromptMetadata(
            title=title,
            description=f"Synced from {file_path}",
            version="1.0.0",
            author="PrompTrek Sync",
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
            tags=[editor_name.lower().replace(" ", "-"), "synced"],
        )

        # Build v2 prompt with raw markdown content
        return UniversalPromptV2(
            schema_version="2.0.0",
            metadata=metadata,
            content=content.strip(),  # Raw markdown content, lossless!
            variables={},
        )

    def _extract_frontmatter(self, content: str) -> tuple[Optional[Dict], str]:
        """
        Extract YAML frontmatter from markdown if present.

        Returns:
            Tuple of (frontmatter_dict, remaining_content)
        """
        if not content.startswith("---"):
            return None, content

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None, content

        try:
            frontmatter = yaml.safe_load(parts[1])
            remaining = parts[2].strip()
            return frontmatter, remaining
        except yaml.YAMLError:
            return None, content

    def _extract_title_from_markdown(self, content: str) -> Optional[str]:
        """Extract title from first H1 heading in markdown."""
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
        return None

    def _parse_markdown_sections(self, content: str) -> Dict[str, List[str]]:
        """
        Parse markdown content and extract instructions by section.

        Args:
            content: Markdown file content

        Returns:
            Dictionary mapping categories to instruction lists
        """
        instructions_dict: Dict[str, List[str]] = {}
        current_section: Optional[str] = None

        lines = content.split("\n")
        for line in lines:
            line_stripped = line.strip()

            # Detect section headers
            if line_stripped.startswith("## "):
                header = line_stripped[3:].lower()
                if "general" in header or "guideline" in header:
                    current_section = "general"
                elif "code" in header and "style" in header:
                    current_section = "code_style"
                elif "test" in header:
                    current_section = "testing"
                elif "security" in header:
                    current_section = "security"
                elif "performance" in header:
                    current_section = "performance"
                elif "architecture" in header:
                    current_section = "architecture"
                else:
                    current_section = "general"
            # Extract bullet points
            elif line_stripped.startswith("- ") or line_stripped.startswith("* "):
                instruction = line_stripped[2:].strip()
                if instruction and current_section:
                    if current_section not in instructions_dict:
                        instructions_dict[current_section] = []
                    instructions_dict[current_section].append(instruction)

        return instructions_dict

    def _extract_context_from_content(self, content: str) -> Optional[ProjectContext]:
        """
        Extract project context information from markdown content.

        Args:
            content: Markdown file content

        Returns:
            ProjectContext if found, None otherwise
        """
        # Simple extraction - look for common patterns
        technologies = []
        project_type = None

        for line in content.split("\n"):
            line_lower = line.lower()
            if "technologies:" in line_lower or "tech stack:" in line_lower:
                # Try to extract tech list
                parts = line.split(":", 1)
                if len(parts) > 1:
                    tech_str = parts[1].strip()
                    # Split by common delimiters
                    for delimiter in [",", "|", "•"]:
                        if delimiter in tech_str:
                            technologies = [
                                t.strip() for t in tech_str.split(delimiter)
                            ]
                            break

        if technologies:
            return ProjectContext(
                project_type=project_type or "application",
                technologies=technologies,
                description=f"Project using {', '.join(technologies)}",
            )

        return None
