"""
Spec inclusion mixin for adapters.

Provides functionality to include spec documents from promptrek/specs/
in generated editor configurations (v3.1.0+ only).
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..core.models import UniversalPrompt, UniversalPromptV2, UniversalPromptV3
from ..utils.spec_manager import SpecManager


class SpecInclusionMixin:
    """Mixin to add spec document inclusion capabilities to adapters."""

    def should_include_specs(
        self, prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]
    ) -> bool:
        """
        Check if spec documents should be included for this prompt.

        Specs are only included for v3.1.0+ prompts (opt-out by default).

        Args:
            prompt: The prompt being generated

        Returns:
            True if specs should be included, False otherwise
        """
        # Only v3.1.0+ prompts support spec inclusion
        if not isinstance(prompt, UniversalPromptV3):
            return False

        # Parse schema version (format: "major.minor.patch")
        try:
            version_parts = prompt.schema_version.split(".")
            major = int(version_parts[0])
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0

            # Require v3.1.0 or greater
            if major < 3 or (major == 3 and minor < 1):
                return False
        except (ValueError, IndexError):
            # Invalid version format, default to not including specs
            return False

        # Check opt-out flag (default is True for v3.1+)
        return getattr(prompt, "include_specs", True)

    def get_spec_documents(self, output_dir: Path) -> List[Dict[str, Any]]:
        """
        Get all spec documents from promptrek/specs/ directory.

        Args:
            output_dir: Project root directory

        Returns:
            List of dicts with keys: id, title, summary, content, path
        """
        spec_manager = SpecManager(output_dir)

        try:
            specs = spec_manager.list_specs()
        except Exception:
            # If registry doesn't exist or can't be read, return empty list
            return []

        spec_docs = []
        for spec in specs:
            try:
                content = spec_manager.get_spec_content(spec.id)
                spec_docs.append(
                    {
                        "id": spec.id,
                        "title": spec.title,
                        "summary": spec.summary or "",
                        "content": content,
                        "path": spec.path,
                        "tags": spec.tags or [],
                    }
                )
            except Exception:
                # Skip specs that can't be read
                continue

        return spec_docs

    def format_spec_as_document_frontmatter(
        self, spec_doc: Dict[str, Any]
    ) -> tuple[str, str]:
        """
        Format a spec document with YAML frontmatter for multi-file editors.

        Args:
            spec_doc: Spec document dict from get_spec_documents()

        Returns:
            Tuple of (filename, full_content_with_frontmatter)
        """
        filename = f"spec-{spec_doc['id']}.md"

        frontmatter_lines = [
            "---",
            f"name: {spec_doc['title']}",
            f"description: {spec_doc['summary']}",
            "alwaysApply: false  # Spec documents are context-specific",
        ]

        # Add tags if present
        if spec_doc.get("tags"):
            tags_str = ", ".join(spec_doc["tags"])
            frontmatter_lines.append(f"tags: [{tags_str}]")

        frontmatter_lines.extend(["---", ""])

        content = "\n".join(frontmatter_lines) + spec_doc["content"]

        return filename, content

    def format_spec_references_section(
        self, spec_docs: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Format spec documents as a reference section for single-file editors.

        Args:
            spec_docs: List of spec document dicts from get_spec_documents()

        Returns:
            Markdown section listing all specs, or None if no specs
        """
        if not spec_docs:
            return None

        lines = [
            "",
            "## Project Specifications",
            "",
            "The following specifications define key aspects of this project. "
            "Reference these when working on related features:",
            "",
        ]

        for spec_doc in spec_docs:
            lines.append(f"### {spec_doc['title']}")
            lines.append(f"**ID:** `{spec_doc['id']}`")
            if spec_doc.get("summary"):
                lines.append(f"**Summary:** {spec_doc['summary']}")
            if spec_doc.get("tags"):
                tags_str = ", ".join(spec_doc["tags"])
                lines.append(f"**Tags:** {tags_str}")
            lines.append(f"**Path:** `{spec_doc['path']}`")
            lines.append("")

            # Include first few lines of content as preview
            content_lines = spec_doc["content"].split("\n")
            # Skip USF header comments and metadata
            preview_start = 0
            for i, line in enumerate(content_lines):
                if line.startswith("---") or line.startswith("<!--"):
                    continue
                if line.strip() and not line.startswith("#"):
                    preview_start = i
                    break

            preview_lines = content_lines[preview_start : preview_start + 5]
            if preview_lines:
                lines.append("```markdown")
                lines.extend(preview_lines)
                if len(content_lines) > preview_start + 5:
                    lines.append("...")
                lines.append("```")
                lines.append("")

        return "\n".join(lines)

    def format_spec_as_comment(self, spec_doc: Dict[str, Any]) -> str:
        """
        Format a spec document as code comments for comment-based editors.

        Args:
            spec_doc: Spec document dict from get_spec_documents()

        Returns:
            Formatted comment string
        """
        lines = [
            f"# Spec: {spec_doc['title']} (ID: {spec_doc['id']})",
        ]

        if spec_doc.get("summary"):
            lines.append(f"# Summary: {spec_doc['summary']}")

        if spec_doc.get("tags"):
            tags_str = ", ".join(spec_doc["tags"])
            lines.append(f"# Tags: {tags_str}")

        lines.append(f"# See: {spec_doc['path']}")

        return "\n".join(lines)
