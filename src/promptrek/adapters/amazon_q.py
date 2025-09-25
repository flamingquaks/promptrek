"""
Amazon Q (comment-based) adapter implementation.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from ..core.exceptions import ValidationError
from ..core.models import UniversalPrompt
from .base import EditorAdapter


class AmazonQAdapter(EditorAdapter):
    """Adapter for Amazon Q comment-based assistance."""

    _description = "Amazon Q (comment-based)"
    _file_patterns = [".amazonq/context.md", ".amazonq/comments.template"]

    def __init__(self):
        super().__init__(
            name="amazon-q",
            description=self._description,
            file_patterns=self._file_patterns,
        )

    def generate(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate Amazon Q configuration files."""

        # Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)

        # Create context content
        context_content = self._build_context(processed_prompt)

        # Create comment templates
        template_content = self._build_comment_templates(processed_prompt)

        # Determine output paths
        amazonq_dir = output_dir / ".amazonq"
        context_file = amazonq_dir / "context.md"
        template_file = amazonq_dir / "comments.template"

        created_files = []

        if dry_run:
            click.echo(f"  📁 Would create: {context_file}")
            click.echo(f"  📁 Would create: {template_file}")
            if verbose:
                click.echo("  📄 Context preview:")
                preview = (
                    context_content[:200] + "..."
                    if len(context_content) > 200
                    else context_content
                )
                click.echo(f"    {preview}")
        else:
            # Create directory and files
            amazonq_dir.mkdir(exist_ok=True)
            with open(context_file, "w", encoding="utf-8") as f:
                f.write(context_content)
            created_files.append(context_file)
            click.echo(f"✅ Generated: {context_file}")

            with open(template_file, "w", encoding="utf-8") as f:
                f.write(template_content)
            created_files.append(template_file)
            click.echo(f"✅ Generated: {template_file}")

        return created_files or [context_file, template_file]

    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """Validate prompt for Amazon Q."""
        errors = []

        # Amazon Q works well with clear documentation and examples
        if not prompt.examples:
            errors.append(
                ValidationError(
                    field="examples",
                    message=(
                        "Amazon Q benefits from code examples for better "
                        "comment-based assistance"
                    ),
                    severity="warning",
                )
            )

        return errors

    def supports_variables(self) -> bool:
        """Amazon Q supports variable substitution."""
        return True

    def supports_conditionals(self) -> bool:
        """Amazon Q supports conditional templates."""
        return True

    def _build_context(self, prompt: UniversalPrompt) -> str:
        """Build Amazon Q context content."""
        lines = []

        # Header
        lines.append(f"# {prompt.metadata.title} - Amazon Q Context")
        lines.append("")
        lines.append("## Project Overview")
        lines.append(prompt.metadata.description)
        lines.append("")

        # Project details
        if prompt.context:
            lines.append("## Project Information")
            if prompt.context.project_type:
                lines.append(f"**Project Type:** {prompt.context.project_type}")
            if prompt.context.technologies:
                tech_list = ", ".join(prompt.context.technologies)
                lines.append(f"**Technologies:** {tech_list}")
            if prompt.context.description:
                lines.append("")
                lines.append("**Description:**")
                lines.append(prompt.context.description)
            lines.append("")

        # Development guidelines for Q
        lines.append("## Amazon Q Guidelines")
        lines.append("")
        lines.append("When using Amazon Q comment-based assistance:")
        lines.append("- Use clear, descriptive comments to request help")
        lines.append("- Provide context about the desired functionality")
        lines.append("- Follow the project's established patterns")
        lines.append("- Ask for specific improvements or implementations")
        lines.append("")

        # Instructions
        if prompt.instructions:
            lines.append("## Development Standards")

            if prompt.instructions.general:
                lines.append("### General Guidelines")
                for instruction in prompt.instructions.general:
                    lines.append(f"- {instruction}")
                lines.append("")

            if prompt.instructions.code_style:
                lines.append("### Code Style")
                for guideline in prompt.instructions.code_style:
                    lines.append(f"- {guideline}")
                lines.append("")

            if prompt.instructions.testing:
                lines.append("### Testing Standards")
                for guideline in prompt.instructions.testing:
                    lines.append(f"- {guideline}")
                lines.append("")

        # Comment-based interaction examples
        lines.append("## Comment Templates")
        lines.append("")
        lines.append("Use these comment patterns to interact with Amazon Q:")
        lines.append("")
        lines.append("```")
        lines.append("// Q: Create a function that handles user authentication")
        lines.append("// Q: Optimize this database query for better performance")
        lines.append("// Q: Add error handling to this API endpoint")
        lines.append("// Q: Generate unit tests for this function")
        lines.append("```")
        lines.append("")

        # Examples if available
        if prompt.examples:
            lines.append("## Code Examples")
            lines.append("")
            lines.append("Reference patterns for Amazon Q assistance:")
            lines.append("")

            for name, example in prompt.examples.items():
                lines.append(f"### {name.replace('_', ' ').title()}")
                lines.append(example)
                lines.append("")

        return "\n".join(lines)

    def _build_comment_templates(self, prompt: UniversalPrompt) -> str:
        """Build Amazon Q comment templates."""
        lines = []

        # Header
        lines.append("# Amazon Q Comment Templates")
        lines.append("")
        lines.append("# Use these comment patterns to request Amazon Q assistance")
        lines.append("")

        # General templates
        lines.append("# === GENERAL ASSISTANCE ===")
        lines.append("")
        lines.append("# Q: Explain this code and suggest improvements")
        lines.append("# Q: Refactor this function for better readability")
        lines.append("# Q: Add comprehensive error handling")
        lines.append("# Q: Generate documentation for this module")
        lines.append("")

        # Technology-specific templates
        if prompt.context and prompt.context.technologies:
            for tech in prompt.context.technologies:
                tech_upper = tech.upper()
                lines.append(f"# === {tech_upper} SPECIFIC ===")
                lines.append("")

                if tech.lower() in ["javascript", "typescript", "node.js"]:
                    lines.append(
                        "# Q: Create an async function with proper error handling"
                    )
                    lines.append("# Q: Optimize this for better performance in Node.js")
                    lines.append("# Q: Add TypeScript types to this function")
                elif tech.lower() in ["python"]:
                    lines.append("# Q: Create a Python class following best practices")
                    lines.append("# Q: Add type hints and docstrings to this function")
                    lines.append("# Q: Optimize this code for better performance")
                elif tech.lower() in ["react", "vue", "angular"]:
                    lines.append(
                        "# Q: Create a reusable component for this functionality"
                    )
                    lines.append("# Q: Add proper state management to this component")
                    lines.append("# Q: Optimize this component for performance")
                elif tech.lower() in ["sql", "postgresql", "mysql"]:
                    lines.append("# Q: Optimize this SQL query for better performance")
                    lines.append("# Q: Add proper indexing strategy for this table")
                    lines.append("# Q: Create a secure parameterized query")
                else:
                    lines.append(f"# Q: Implement {tech} best practices in this code")
                    lines.append(f"# Q: Optimize this {tech} implementation")
                    lines.append(f"# Q: Add {tech}-specific error handling")

                lines.append("")

        # Testing templates
        if prompt.instructions and prompt.instructions.testing:
            lines.append("# === TESTING ===")
            lines.append("")
            lines.append("# Q: Generate comprehensive unit tests for this function")
            lines.append("# Q: Create integration tests for this API endpoint")
            lines.append("# Q: Add mock objects for this test scenario")
            lines.append("# Q: Generate test data for this test case")
            lines.append("")

        # Security templates
        lines.append("# === SECURITY ===")
        lines.append("")
        lines.append("# Q: Review this code for security vulnerabilities")
        lines.append("# Q: Add input validation and sanitization")
        lines.append("# Q: Implement secure authentication for this endpoint")
        lines.append("# Q: Add rate limiting to this API")
        lines.append("")

        # Performance templates
        lines.append("# === PERFORMANCE ===")
        lines.append("")
        lines.append("# Q: Optimize this code for better performance")
        lines.append("# Q: Add caching to improve response times")
        lines.append("# Q: Reduce memory usage in this implementation")
        lines.append("# Q: Profile and optimize this algorithm")

        return "\n".join(lines)
