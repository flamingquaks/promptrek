"""
JetBrains AI adapter implementation.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from ..core.exceptions import ValidationError
from ..core.models import UniversalPrompt
from .base import EditorAdapter
from .sync_mixin import MarkdownSyncMixin


class JetBrainsAdapter(MarkdownSyncMixin, EditorAdapter):
    """Adapter for JetBrains AI assistance."""

    _description = "JetBrains AI (.assistant/rules/)"
    _file_patterns = [".assistant/rules/*.md"]

    def __init__(self) -> None:
        super().__init__(
            name="jetbrains",
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
        headless: bool = False,
    ) -> List[Path]:
        """Generate JetBrains AI configuration files."""

        # Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)

        # Process conditionals if supported
        conditional_content = self.process_conditionals(processed_prompt, variables)

        # Generate rules directory system
        rules_files = self._generate_rules_system(
            processed_prompt, conditional_content, output_dir, dry_run, verbose
        )

        return rules_files

    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """Validate prompt for JetBrains AI."""
        errors = []

        # JetBrains works well with structured development guidelines
        if not prompt.instructions:
            errors.append(
                ValidationError(
                    field="instructions",
                    message="JetBrains AI benefits from structured development guidelines",
                    severity="warning",
                )
            )

        return errors

    def supports_variables(self) -> bool:
        """JetBrains supports variable substitution."""
        return True

    def supports_conditionals(self) -> bool:
        """JetBrains supports conditional configuration."""
        return True

    def parse_files(self, source_dir: Path) -> UniversalPrompt:
        """Parse JetBrains files back into a UniversalPrompt."""
        return self.parse_markdown_rules_files(
            source_dir=source_dir,
            rules_subdir=".assistant/rules",
            file_extension="md",
            editor_name="JetBrains AI",
        )

    def _generate_rules_system(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate .assistant/rules/ directory with markdown files."""
        rules_dir = output_dir / ".assistant" / "rules"
        created_files = []

        # Generate general coding rules
        all_instructions = []
        if prompt.instructions and prompt.instructions.general:
            all_instructions.extend(prompt.instructions.general)
        if (
            conditional_content
            and "instructions" in conditional_content
            and "general" in conditional_content["instructions"]
        ):
            all_instructions.extend(conditional_content["instructions"]["general"])

        if all_instructions:
            general_file = rules_dir / "general.md"
            general_content = self._build_rules_content(
                "General Coding Rules", all_instructions
            )

            if dry_run:
                click.echo(f"  📁 Would create: {general_file}")
                if verbose:
                    preview = (
                        general_content[:200] + "..."
                        if len(general_content) > 200
                        else general_content
                    )
                    click.echo(f"    {preview}")
                created_files.append(general_file)
            else:
                rules_dir.mkdir(parents=True, exist_ok=True)
                with open(general_file, "w", encoding="utf-8") as f:
                    f.write(general_content)
                click.echo(f"✅ Generated: {general_file}")
                created_files.append(general_file)

        # Generate code style rules
        if prompt.instructions and prompt.instructions.code_style:
            style_file = rules_dir / "code-style.md"
            style_content = self._build_rules_content(
                "Code Style Rules", prompt.instructions.code_style
            )

            if dry_run:
                click.echo(f"  📁 Would create: {style_file}")
                if verbose:
                    preview = (
                        style_content[:200] + "..."
                        if len(style_content) > 200
                        else style_content
                    )
                    click.echo(f"    {preview}")
                created_files.append(style_file)
            else:
                rules_dir.mkdir(parents=True, exist_ok=True)
                with open(style_file, "w", encoding="utf-8") as f:
                    f.write(style_content)
                click.echo(f"✅ Generated: {style_file}")
                created_files.append(style_file)

        # Generate testing rules
        if prompt.instructions and prompt.instructions.testing:
            testing_file = rules_dir / "testing.md"
            testing_content = self._build_rules_content(
                "Testing Rules", prompt.instructions.testing
            )

            if dry_run:
                click.echo(f"  📁 Would create: {testing_file}")
                if verbose:
                    preview = (
                        testing_content[:200] + "..."
                        if len(testing_content) > 200
                        else testing_content
                    )
                    click.echo(f"    {preview}")
                created_files.append(testing_file)
            else:
                rules_dir.mkdir(parents=True, exist_ok=True)
                with open(testing_file, "w", encoding="utf-8") as f:
                    f.write(testing_content)
                click.echo(f"✅ Generated: {testing_file}")
                created_files.append(testing_file)

        # Generate technology-specific rules
        if prompt.context and prompt.context.technologies:
            for tech in prompt.context.technologies[:2]:  # Limit to 2 main technologies
                tech_file = rules_dir / f"{tech.lower()}-rules.md"
                tech_content = self._build_tech_rules_content(tech, prompt)

                if dry_run:
                    click.echo(f"  📁 Would create: {tech_file}")
                    if verbose:
                        preview = (
                            tech_content[:200] + "..."
                            if len(tech_content) > 200
                            else tech_content
                        )
                        click.echo(f"    {preview}")
                    created_files.append(tech_file)
                else:
                    rules_dir.mkdir(parents=True, exist_ok=True)
                    with open(tech_file, "w", encoding="utf-8") as f:
                        f.write(tech_content)
                    click.echo(f"✅ Generated: {tech_file}")
                    created_files.append(tech_file)

        return created_files

    def _build_rules_content(self, title: str, instructions: List[str]) -> str:
        """Build markdown rules content for .assistant/rules/ files."""
        lines = []

        lines.append(f"# {title}")
        lines.append("")

        for instruction in instructions:
            lines.append(f"- {instruction}")

        lines.append("")
        lines.append("## Additional Guidelines")
        lines.append("- Follow project-specific patterns and conventions")
        lines.append("- Maintain consistency with existing codebase")
        lines.append("- Consider performance and security implications")

        return "\n".join(lines)

    def _build_tech_rules_content(self, tech: str, prompt: UniversalPrompt) -> str:
        """Build technology-specific rules content."""
        lines = []

        lines.append(f"# {tech.title()} Rules")
        lines.append("")

        # Add general instructions that apply to this tech
        if prompt.instructions and prompt.instructions.general:
            lines.append("## General Guidelines")
            for instruction in prompt.instructions.general:
                lines.append(f"- {instruction}")
            lines.append("")

        # Add tech-specific best practices
        lines.append(f"## {tech.title()} Best Practices")
        tech_practices = {
            "java": [
                "Follow Java coding conventions",
                "Use meaningful names for classes, methods, and variables",
                "Implement proper exception handling",
                "Leverage modern Java features appropriately",
            ],
            "kotlin": [
                "Use Kotlin idioms and best practices",
                "Prefer immutability with val over var",
                "Leverage null safety features",
                "Use extension functions appropriately",
            ],
            "python": [
                "Follow PEP 8 style guidelines",
                "Use type hints for function signatures",
                "Implement proper error handling with try/except blocks",
                "Use docstrings for all functions and classes",
            ],
            "javascript": [
                "Use modern ES6+ syntax",
                "Prefer const and let over var",
                "Use arrow functions appropriately",
                "Implement proper error handling with try/catch blocks",
            ],
        }

        if tech.lower() in tech_practices:
            for practice in tech_practices[tech.lower()]:
                lines.append(f"- {practice}")
        else:
            lines.append(f"- Follow {tech} best practices and conventions")
            lines.append(f"- Maintain consistency with existing {tech} code")
            lines.append(f"- Use {tech} idioms and patterns appropriately")

        return "\n".join(lines)
