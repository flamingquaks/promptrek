"""
Amazon Q adapter implementation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import click

from ..core.exceptions import ValidationError
from ..core.models import UniversalPrompt, UniversalPromptV2
from .base import EditorAdapter
from .sync_mixin import MarkdownSyncMixin

# Maximum number of instructions to include in agent configuration
MAX_AGENT_INSTRUCTIONS = 3


class AmazonQAdapter(MarkdownSyncMixin, EditorAdapter):
    """Adapter for Amazon Q AI assistant."""

    _description = "Amazon Q (.amazonq/rules/, .amazonq/cli-agents/)"
    _file_patterns = [".amazonq/rules/*.md", ".amazonq/cli-agents/*.json"]

    def __init__(self) -> None:
        super().__init__(
            name="amazon-q",
            description=self._description,
            file_patterns=self._file_patterns,
        )

    def generate(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2],
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> List[Path]:
        """Generate Amazon Q configuration files."""

        # V2: Use documents field for multi-file rules or main content for single file
        if isinstance(prompt, UniversalPromptV2):
            return self._generate_v2(prompt, output_dir, dry_run, verbose, variables)

        # V1: Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)

        # Process conditionals if supported
        conditional_content = self.process_conditionals(processed_prompt, variables)

        created_files = []

        # Generate rules directory system
        rules_files = self._generate_rules_system(
            processed_prompt, conditional_content, output_dir, dry_run, verbose
        )
        created_files.extend(rules_files)

        # Generate CLI agents if headless is enabled
        if headless:
            agent_files = self._generate_cli_agents(
                processed_prompt, output_dir, dry_run, verbose
            )
            created_files.extend(agent_files)

        return created_files

    def _generate_v2(
        self,
        prompt: UniversalPromptV2,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate Amazon Q files from v2 schema (using documents for rules or content for single file)."""
        rules_dir = output_dir / ".amazonq" / "rules"
        created_files = []

        # If documents field is present, generate separate rule files
        if prompt.documents:
            for doc in prompt.documents:
                # Apply variable substitution
                content = doc.content
                if variables:
                    for var_name, var_value in variables.items():
                        placeholder = "{{{ " + var_name + " }}}"
                        content = content.replace(placeholder, var_value)

                # Generate filename from document name
                filename = (
                    f"{doc.name}.md" if not doc.name.endswith(".md") else doc.name
                )
                output_file = rules_dir / filename

                if dry_run:
                    click.echo(f"  📁 Would create: {output_file}")
                    if verbose:
                        preview = (
                            content[:200] + "..." if len(content) > 200 else content
                        )
                        click.echo(f"    {preview}")
                    created_files.append(output_file)
                else:
                    rules_dir.mkdir(parents=True, exist_ok=True)
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    click.echo(f"✅ Generated: {output_file}")
                    created_files.append(output_file)
        else:
            # No documents, use main content as general.md
            content = prompt.content
            if variables:
                for var_name, var_value in variables.items():
                    placeholder = "{{{ " + var_name + " }}}"
                    content = content.replace(placeholder, var_value)

            output_file = rules_dir / "general.md"

            if dry_run:
                click.echo(f"  📁 Would create: {output_file}")
                if verbose:
                    preview = content[:200] + "..." if len(content) > 200 else content
                    click.echo(f"    {preview}")
                created_files.append(output_file)
            else:
                rules_dir.mkdir(parents=True, exist_ok=True)
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(content)
                click.echo(f"✅ Generated: {output_file}")
                created_files.append(output_file)

        return created_files

    def _generate_rules_system(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate .amazonq/rules/ directory with markdown files."""
        rules_dir = output_dir / ".amazonq" / "rules"
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

        # Generate security rules if defined
        if prompt.instructions and prompt.instructions.security:
            security_file = rules_dir / "security.md"
            security_content = self._build_rules_content(
                "Security Rules", prompt.instructions.security
            )

            if dry_run:
                click.echo(f"  📁 Would create: {security_file}")
                if verbose:
                    preview = (
                        security_content[:200] + "..."
                        if len(security_content) > 200
                        else security_content
                    )
                    click.echo(f"    {preview}")
                created_files.append(security_file)
            else:
                rules_dir.mkdir(parents=True, exist_ok=True)
                with open(security_file, "w", encoding="utf-8") as f:
                    f.write(security_content)
                click.echo(f"✅ Generated: {security_file}")
                created_files.append(security_file)

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

    def _generate_cli_agents(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate .amazonq/cli-agents/ directory with agent JSON files."""
        agents_dir = output_dir / ".amazonq" / "cli-agents"
        created_files = []

        # Generate default agents based on instructions
        agents = []

        # Code review agent
        if prompt.instructions and prompt.instructions.code_style:
            agents.append(
                {
                    "name": "code-review-agent",
                    "description": "Reviews code for style and quality issues",
                    "instructions": "Focus on code style, readability, and best practices. "
                    + " ".join(prompt.instructions.code_style[:MAX_AGENT_INSTRUCTIONS]),
                }
            )

        # Security review agent
        if prompt.instructions and prompt.instructions.security:
            agents.append(
                {
                    "name": "security-review-agent",
                    "description": "Reviews code for security vulnerabilities",
                    "instructions": "Always focus on OWASP Top 10 vulnerabilities. "
                    + " ".join(prompt.instructions.security[:3]),
                }
            )

        # Testing agent
        if prompt.instructions and prompt.instructions.testing:
            agents.append(
                {
                    "name": "test-generation-agent",
                    "description": "Generates unit and integration tests",
                    "instructions": "Follow testing best practices. "
                    + " ".join(prompt.instructions.testing[:3]),
                }
            )

        # Generate agent files
        for agent in agents:
            agent_file = agents_dir / f"{agent['name']}.json"
            agent_content = json.dumps(agent, indent=2)

            if dry_run:
                click.echo(f"  📁 Would create: {agent_file}")
                if verbose:
                    click.echo(f"    {agent_content[:150]}...")
                created_files.append(agent_file)
            else:
                agents_dir.mkdir(parents=True, exist_ok=True)
                with open(agent_file, "w", encoding="utf-8") as f:
                    f.write(agent_content)
                click.echo(f"✅ Generated: {agent_file}")
                created_files.append(agent_file)

        return created_files

    def _build_rules_content(self, title: str, instructions: List[str]) -> str:
        """Build markdown rules content for .amazonq/rules/ files."""
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
            "typescript": [
                "Use strict TypeScript configuration",
                "Prefer interfaces over types for object shapes",
                "Use proper typing for all function parameters and returns",
                "Leverage TypeScript's utility types when appropriate",
            ],
            "java": [
                "Follow Java coding conventions",
                "Use meaningful names for classes, methods, and variables",
                "Implement proper exception handling",
                "Leverage modern Java features appropriately",
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

    def validate(
        self, prompt: Union[UniversalPrompt, UniversalPromptV2]
    ) -> List[ValidationError]:
        """Validate prompt for Amazon Q."""
        errors = []

        # V2 validation: check content exists
        if isinstance(prompt, UniversalPromptV2):
            if not prompt.content or not prompt.content.strip():
                errors.append(
                    ValidationError(
                        field="content",
                        message="Amazon Q requires content",
                        severity="error",
                    )
                )
            return errors

        # V1 validation: Amazon Q works well with structured instructions
        if not prompt.instructions:
            errors.append(
                ValidationError(
                    field="instructions",
                    message="Amazon Q benefits from structured instructions",
                    severity="warning",
                )
            )

        return errors

    def supports_variables(self) -> bool:
        """Amazon Q supports variable substitution."""
        return True

    def supports_conditionals(self) -> bool:
        """Amazon Q supports conditional configuration."""
        return True

    def parse_files(
        self, source_dir: Path
    ) -> Union[UniversalPrompt, UniversalPromptV2]:
        """Parse Amazon Q files back into a UniversalPrompt or UniversalPromptV2."""
        return self.parse_markdown_rules_files(
            source_dir=source_dir,
            rules_subdir=".amazonq/rules",
            file_extension="md",
            editor_name="Amazon Q",
        )
