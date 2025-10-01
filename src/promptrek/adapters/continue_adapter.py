"""
Continue editor adapter implementation.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import yaml

from ..core.exceptions import ValidationError
from ..core.models import Instructions, ProjectContext, PromptMetadata, UniversalPrompt
from .base import EditorAdapter


class ContinueAdapter(EditorAdapter):
    """Adapter for Continue editor."""

    _description = "Continue (.continue/rules/)"
    _file_patterns = [".continue/rules/*.md"]

    def __init__(self):
        super().__init__(
            name="continue",
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
        """Generate Continue configuration files."""

        # Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)

        # Process conditionals if supported
        conditional_content = self.process_conditionals(processed_prompt, variables)

        # Generate rules directory system
        rules_files = self._generate_rules_system(
            processed_prompt, conditional_content, output_dir, dry_run, verbose
        )

        return rules_files

    def _generate_rules_system(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate .continue/rules/ directory with markdown files."""
        rules_dir = output_dir / ".continue" / "rules"
        created_files = []

        # Generate general coding rules
        # Collect all instructions (original + conditional)
        all_instructions = []
        if prompt.instructions and prompt.instructions.general:
            all_instructions.extend(prompt.instructions.general)
        # Add conditional general instructions
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

    def _generate_legacy_rules(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate legacy .continuerules for backward compatibility."""
        content = self._build_legacy_rules_content(prompt)
        output_file = output_dir / ".continuerules"

        if dry_run:
            click.echo(f"  📁 Would create: {output_file} (legacy compatibility)")
            if verbose:
                preview = content[:200] + "..." if len(content) > 200 else content
                click.echo(f"    {preview}")
        else:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"✅ Generated: {output_file} (legacy compatibility)")
            return [output_file]

        return []

    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """Validate prompt for Continue."""
        errors = []

        # Continue requires a system message
        if not prompt.metadata.description:
            errors.append(
                ValidationError(
                    field="metadata.description",
                    message="Continue requires a description for the system message",
                )
            )

        return errors

    def supports_variables(self) -> bool:
        """Continue supports variable substitution."""
        return True

    def supports_conditionals(self) -> bool:
        """Continue supports conditional configuration."""
        return True

    def _build_rules_content(self, title: str, instructions: List[str]) -> str:
        """Build markdown rules content for .continue/rules/ files."""
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
            "typescript": [
                "Use strict TypeScript configuration",
                "Prefer interfaces over types for object shapes",
                "Use proper typing for all function parameters and returns",
                "Leverage TypeScript's utility types when appropriate",
            ],
            "react": [
                "Use functional components with hooks",
                "Implement proper prop typing with TypeScript",
                "Follow React best practices for state management",
                "Use React.memo for performance optimization when needed",
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
            "node": [
                "Use async/await for asynchronous operations",
                "Implement proper error handling middleware",
                "Follow Node.js best practices for API design",
                "Use environment variables for configuration",
            ],
        }

        if tech.lower() in tech_practices:
            for practice in tech_practices[tech.lower()]:
                lines.append(f"- {practice}")
        else:
            lines.append(f"- Follow {tech} best practices and conventions")
            lines.append(f"- Maintain consistency with existing {tech} code")
            lines.append(f"- Use {tech} idioms and patterns appropriately")

        lines.append("")
        lines.append(f"## {tech.title()} Code Generation Guidelines")
        lines.append(f"- Generate {tech} code that follows established patterns")
        lines.append(f"- Include appropriate {tech} documentation and comments")
        lines.append(f"- Consider {tech} performance optimization techniques")

        return "\n".join(lines)

    def _build_legacy_rules_content(self, prompt: UniversalPrompt) -> str:
        """Build legacy .continuerules content for backward compatibility."""
        lines = []

        lines.append(f"# {prompt.metadata.title} - Continue Rules")
        lines.append("")
        lines.append(prompt.metadata.description)
        lines.append("")

        # Project Context
        if prompt.context:
            lines.append("## Project Context")
            if prompt.context.project_type:
                lines.append(f"**Type:** {prompt.context.project_type}")
            if prompt.context.technologies:
                lines.append(
                    f"**Technologies:** {', '.join(prompt.context.technologies)}"
                )
            if prompt.context.description:
                lines.append("")
                lines.append("**Description:**")
                lines.append(prompt.context.description)
            lines.append("")

        # Instructions
        if prompt.instructions:
            if prompt.instructions.general:
                lines.append("## General Rules")
                for instruction in prompt.instructions.general:
                    lines.append(f"- {instruction}")
                lines.append("")

            if prompt.instructions.code_style:
                lines.append("## Code Style Rules")
                for guideline in prompt.instructions.code_style:
                    lines.append(f"- {guideline}")
                lines.append("")

            if prompt.instructions.testing:
                lines.append("## Testing Rules")
                for guideline in prompt.instructions.testing:
                    lines.append(f"- {guideline}")
                lines.append("")

        # Continue-specific guidance
        lines.append("## Continue AI Guidelines")
        lines.append("- Provide contextually aware code suggestions")
        lines.append("- Follow established project patterns and conventions")
        lines.append("- Generate comprehensive documentation for complex logic")
        lines.append("- Consider performance implications in suggestions")
        if prompt.context and prompt.context.technologies:
            tech_list = ", ".join(prompt.context.technologies)
            lines.append(f"- Leverage {tech_list} best practices and idioms")

        return "\n".join(lines)

    def parse_files(self, source_dir: Path) -> UniversalPrompt:
        """
        Parse Continue files back into a UniversalPrompt.

        Args:
            source_dir: Directory containing Continue configuration files

        Returns:
            UniversalPrompt object parsed from Continue files
        """
        # Initialize parsed data
        metadata = PromptMetadata(
            title="Continue AI Assistant",
            description="Configuration parsed from Continue files",
            version="1.0.0",
            author="PrompTrek Sync",
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
            tags=["continue", "synced"],
        )

        instructions = Instructions()
        technologies = []

        # Parse config.yaml if it exists
        config_file = source_dir / "config.yaml"
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)

                if config and isinstance(config, dict):
                    # Update metadata from config
                    if "name" in config:
                        metadata.title = config["name"]
                    if "systemMessage" in config:
                        metadata.description = (
                            config["systemMessage"].split("\n\n", 1)[-1]
                            if "\n\n" in config["systemMessage"]
                            else config["systemMessage"]
                        )

                    # Extract rules as general instructions
                    if "rules" in config and isinstance(config["rules"], list):
                        instructions.general = config["rules"]

            except Exception as e:
                click.echo(f"Warning: Could not parse config.yaml: {e}")

        # Parse markdown files from .continue/rules/
        rules_dir = source_dir / ".continue" / "rules"
        if rules_dir.exists():
            instructions_dict = {}

            for md_file in rules_dir.glob("*.md"):
                try:
                    instructions_from_file = self._parse_markdown_file(md_file)

                    # Map file names to instruction categories
                    filename = md_file.stem
                    if filename == "general":
                        instructions_dict["general"] = instructions_from_file
                    elif filename == "code-style":
                        instructions_dict["code_style"] = instructions_from_file
                    elif filename == "testing":
                        instructions_dict["testing"] = instructions_from_file
                    elif filename == "security":
                        instructions_dict["security"] = instructions_from_file
                    elif filename == "performance":
                        instructions_dict["performance"] = instructions_from_file
                    elif filename == "architecture":
                        instructions_dict["architecture"] = instructions_from_file
                    elif filename.endswith("-rules"):
                        # Technology-specific rules
                        tech = filename.replace("-rules", "")
                        technologies.append(tech)
                        # Add to general instructions for now
                        if "general" not in instructions_dict:
                            instructions_dict["general"] = []
                        instructions_dict["general"].extend(instructions_from_file)
                    else:
                        # Unknown file, add to general instructions
                        if "general" not in instructions_dict:
                            instructions_dict["general"] = []
                        instructions_dict["general"].extend(instructions_from_file)

                except Exception as e:
                    click.echo(f"Warning: Could not parse {md_file}: {e}")

            # Merge config.yaml rules with markdown rules
            if instructions.general and "general" in instructions_dict:
                # Combine and deduplicate
                combined_general = list(instructions.general)
                for instruction in instructions_dict["general"]:
                    if instruction not in combined_general:
                        combined_general.append(instruction)
                instructions_dict["general"] = combined_general
            elif instructions.general and "general" not in instructions_dict:
                instructions_dict["general"] = list(instructions.general)

            # Update instructions object
            for category, instrs in instructions_dict.items():
                if instrs:
                    setattr(instructions, category, instrs)

        # Create context if technologies were found
        context = None
        if technologies:
            context = ProjectContext(
                project_type="application",
                technologies=technologies,
                description=f"Project using {', '.join(technologies)}",
            )

        return UniversalPrompt(
            schema_version="1.0.0",
            metadata=metadata,
            targets=["continue"],
            context=context,
            instructions=instructions,
        )

    def _parse_markdown_file(self, md_file: Path) -> List[str]:
        """
        Parse markdown file and extract bullet point instructions.

        Args:
            md_file: Path to markdown file

        Returns:
            List of instructions extracted from the file
        """
        instructions = []

        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract bullet points (lines starting with -)
        # Skip the generic guidelines that are added by the generator
        generic_guidelines = {
            "Follow project-specific patterns and conventions",
            "Maintain consistency with existing codebase",
            "Consider performance and security implications",
        }

        for line in content.split("\n"):
            line = line.strip()
            # Only process lines that start with "- " (not indented bullets)
            if line.startswith("- ") and not line.startswith("  -"):
                # Remove the bullet point marker and clean up
                instruction = line[2:].strip()
                if (
                    instruction
                    and instruction not in instructions
                    and instruction not in generic_guidelines
                ):
                    instructions.append(instruction)

        return instructions
