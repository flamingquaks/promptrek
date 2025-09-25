"""
Cursor editor adapter implementation.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from ..core.exceptions import ValidationError
from ..core.models import UniversalPrompt
from .base import EditorAdapter


class CursorAdapter(EditorAdapter):
    """Adapter for Cursor editor."""

    _description = "Cursor (.cursor/rules/, AGENTS.md)"
    _file_patterns = [".cursor/rules/*.mdc", "AGENTS.md"]

    def __init__(self):
        super().__init__(
            name="cursor",
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
        """Generate Cursor configuration files."""

        # Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)

        created_files = []

        # Generate modern .cursor/rules/ system
        rules_files = self._generate_rules_system(
            processed_prompt, output_dir, dry_run, verbose
        )
        created_files.extend(rules_files)

        # Generate AGENTS.md for simple agent instructions
        agents_file = self._generate_agents_file(
            processed_prompt, output_dir, dry_run, verbose
        )
        created_files.extend(agents_file)

        # Generate ignore files for better indexing control
        ignore_files = self._generate_ignore_files(
            processed_prompt, output_dir, dry_run, verbose
        )
        created_files.extend(ignore_files)

        return created_files

    def _generate_rules_system(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate modern .cursor/rules/ system with .mdc files."""
        rules_dir = output_dir / ".cursor" / "rules"
        created_files = []

        # Create general coding standards rule
        if prompt.instructions and prompt.instructions.code_style:
            coding_file = rules_dir / "coding-standards.mdc"
            coding_content = self._build_mdc_content(
                "Coding Standards",
                prompt.instructions.code_style,
                "**/*.{ts,tsx,js,jsx,py,java,go,rs,cpp,c,h}",
                "Apply coding standards to all source files",
            )

            if dry_run:
                click.echo(f"  📁 Would create: {coding_file}")
                if verbose:
                    preview = (
                        coding_content[:200] + "..."
                        if len(coding_content) > 200
                        else coding_content
                    )
                    click.echo(f"    {preview}")
                created_files.append(coding_file)
            else:
                rules_dir.mkdir(parents=True, exist_ok=True)
                with open(coding_file, "w", encoding="utf-8") as f:
                    f.write(coding_content)
                click.echo(f"✅ Generated: {coding_file}")
                created_files.append(coding_file)

        # Create testing guidelines rule
        if prompt.instructions and prompt.instructions.testing:
            testing_file = rules_dir / "testing-guidelines.mdc"
            testing_content = self._build_mdc_content(
                "Testing Guidelines",
                prompt.instructions.testing,
                "**/*.{test,spec}.{ts,tsx,js,jsx,py}",
                "Apply testing guidelines to test files",
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

        # Create technology-specific rules if context provided
        if prompt.context and prompt.context.technologies:
            for tech in prompt.context.technologies[:3]:  # Limit to 3 main technologies
                tech_file = rules_dir / f"{tech.lower()}-guidelines.mdc"
                tech_content = self._build_tech_mdc_content(tech, prompt)

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

    def _generate_agents_file(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate AGENTS.md file for simple agent instructions."""
        agents_file = output_dir / "AGENTS.md"
        content = self._build_agents_content(prompt)

        if dry_run:
            click.echo(f"  📁 Would create: {agents_file}")
            if verbose:
                click.echo("  📄 AGENTS.md preview:")
                preview = content[:200] + "..." if len(content) > 200 else content
                click.echo(f"    {preview}")
            return [agents_file]
        else:
            with open(agents_file, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"✅ Generated: {agents_file}")
            return [agents_file]

    def _generate_legacy_cursorrules(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate legacy .cursorrules for backward compatibility."""
        # Create content
        content = self._build_legacy_content(prompt)

        # Determine output path
        output_file = output_dir / ".cursorrules"

        if dry_run:
            click.echo(f"  📁 Would create: {output_file} (legacy compatibility)")
            if verbose:
                click.echo("  📄 Content preview:")
                preview = content[:200] + "..." if len(content) > 200 else content
                click.echo(f"    {preview}")
        else:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"✅ Generated: {output_file} (legacy compatibility)")
            return [output_file]

        return []

    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """Validate prompt for Cursor."""
        errors = []

        # Cursor works well with structured instructions
        if not prompt.instructions:
            errors.append(
                ValidationError(
                    field="instructions",
                    message="Cursor works best with structured instructions",
                )
            )

        return errors

    def supports_variables(self) -> bool:
        """Cursor supports variable substitution."""
        return True

    def supports_conditionals(self) -> bool:
        """Cursor supports conditional instructions."""
        return True

    def _build_mdc_content(
        self, title: str, instructions: List[str], globs: str, description: str
    ) -> str:
        """Build .mdc file content with YAML frontmatter."""
        lines = []

        # YAML frontmatter
        lines.append("---")
        lines.append(f"description: {description}")
        lines.append(f'globs: "{globs}"')
        lines.append("alwaysApply: false")
        lines.append("---")
        lines.append("")

        # Content
        lines.append(f"# {title}")
        lines.append("")

        for instruction in instructions:
            lines.append(f"- {instruction}")

        return "\n".join(lines)

    def _build_tech_mdc_content(self, tech: str, prompt: UniversalPrompt) -> str:
        """Build technology-specific .mdc content."""
        lines = []

        # Determine file patterns based on technology
        tech_patterns = {
            "typescript": "**/*.{ts,tsx}",
            "javascript": "**/*.{js,jsx}",
            "python": "**/*.py",
            "react": "**/*.{tsx,jsx}",
            "node": "**/*.{js,ts}",
            "go": "**/*.go",
            "rust": "**/*.rs",
            "java": "**/*.java",
            "cpp": "**/*.{cpp,c,h}",
        }

        pattern = tech_patterns.get(tech.lower(), "**/*")

        # YAML frontmatter
        lines.append("---")
        lines.append(f"description: {tech} specific guidelines")
        lines.append(f'globs: "{pattern}"')
        lines.append("alwaysApply: false")
        lines.append("---")
        lines.append("")

        # Content
        lines.append(f"# {tech.title()} Guidelines")
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
            ],
            "react": [
                "Use functional components with hooks",
                "Implement proper prop typing with TypeScript",
                "Follow React best practices for state management",
            ],
            "python": [
                "Follow PEP 8 style guidelines",
                "Use type hints for function signatures",
                "Implement proper error handling with try/except blocks",
            ],
        }

        if tech.lower() in tech_practices:
            for practice in tech_practices[tech.lower()]:
                lines.append(f"- {practice}")
        else:
            lines.append(f"- Follow {tech} best practices and conventions")
            lines.append(f"- Maintain consistency with existing {tech} code")

        return "\n".join(lines)

    def _build_agents_content(self, prompt: UniversalPrompt) -> str:
        """Build AGENTS.md content for simple agent instructions."""
        lines = []

        lines.append(f"# {prompt.metadata.title}")
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
                lines.append("## General Instructions")
                for instruction in prompt.instructions.general:
                    lines.append(f"- {instruction}")
                lines.append("")

            if prompt.instructions.code_style:
                lines.append("## Code Style")
                for guideline in prompt.instructions.code_style:
                    lines.append(f"- {guideline}")
                lines.append("")

            if prompt.instructions.testing:
                lines.append("## Testing Standards")
                for guideline in prompt.instructions.testing:
                    lines.append(f"- {guideline}")
                lines.append("")

        return "\n".join(lines)

    def _generate_ignore_files(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate Cursor ignore files for better indexing control."""
        created_files = []

        # Generate .cursorignore for files to ignore completely
        cursorignore_content = self._build_cursorignore_content(prompt)
        cursorignore_file = output_dir / ".cursorignore"

        if dry_run:
            click.echo(f"  📁 Would create: {cursorignore_file}")
            if verbose:
                preview = (
                    cursorignore_content[:200] + "..."
                    if len(cursorignore_content) > 200
                    else cursorignore_content
                )
                click.echo(f"    {preview}")
            created_files.append(cursorignore_file)
        else:
            with open(cursorignore_file, "w", encoding="utf-8") as f:
                f.write(cursorignore_content)
            click.echo(f"✅ Generated: {cursorignore_file}")
            created_files.append(cursorignore_file)

        # Generate .cursorindexingignore for indexing control
        indexignore_content = self._build_indexing_ignore_content(prompt)
        indexignore_file = output_dir / ".cursorindexingignore"

        if dry_run:
            click.echo(f"  📁 Would create: {indexignore_file}")
            if verbose:
                preview = (
                    indexignore_content[:200] + "..."
                    if len(indexignore_content) > 200
                    else indexignore_content
                )
                click.echo(f"    {preview}")
            created_files.append(indexignore_file)
        else:
            with open(indexignore_file, "w", encoding="utf-8") as f:
                f.write(indexignore_content)
            click.echo(f"✅ Generated: {indexignore_file}")
            created_files.append(indexignore_file)

        return created_files

    def _build_cursorignore_content(self, prompt: UniversalPrompt) -> str:
        """Build .cursorignore content for files to exclude from Cursor."""
        lines = []

        lines.append("# Cursor ignore file - files to exclude from analysis")
        lines.append("# Generated by PrompTrek")
        lines.append("")

        # Standard ignore patterns
        lines.append("# Dependencies")
        lines.append("node_modules/")
        lines.append("__pycache__/")
        lines.append("*.pyc")
        lines.append("venv/")
        lines.append("env/")
        lines.append(".env")
        lines.append("")

        lines.append("# Build outputs")
        lines.append("dist/")
        lines.append("build/")
        lines.append("*.min.js")
        lines.append("*.map")
        lines.append("")

        lines.append("# IDE and editor files")
        lines.append(".vscode/settings.json")
        lines.append(".idea/")
        lines.append("*.swp")
        lines.append("*.swo")
        lines.append("")

        lines.append("# Logs and temporary files")
        lines.append("*.log")
        lines.append("*.tmp")
        lines.append("tmp/")
        lines.append("temp/")
        lines.append("")

        # Technology-specific ignore patterns
        if prompt.context and prompt.context.technologies:
            for tech in prompt.context.technologies:
                tech_lower = tech.lower()
                if tech_lower in ["react", "typescript", "javascript", "node"]:
                    lines.append("# JavaScript/Node.js specific")
                    lines.append("coverage/")
                    lines.append("*.tsbuildinfo")
                    lines.append("npm-debug.log*")
                    lines.append("")
                elif tech_lower == "python":
                    lines.append("# Python specific")
                    lines.append("*.egg-info/")
                    lines.append(".pytest_cache/")
                    lines.append(".coverage")
                    lines.append("")
                elif tech_lower in ["java", "kotlin"]:
                    lines.append("# Java/Kotlin specific")
                    lines.append("target/")
                    lines.append("*.class")
                    lines.append("*.jar")
                    lines.append("")

        return "\n".join(lines)

    def _build_indexing_ignore_content(self, prompt: UniversalPrompt) -> str:
        """Build .cursorindexingignore content for indexing control."""
        lines = []

        lines.append(
            "# Cursor indexing ignore - files to exclude from indexing but not analysis"
        )
        lines.append("# Generated by PrompTrek")
        lines.append("")

        # Large files and generated content
        lines.append("# Large files and generated content")
        lines.append("*.lock")
        lines.append("package-lock.json")
        lines.append("yarn.lock")
        lines.append("Pipfile.lock")
        lines.append("poetry.lock")
        lines.append("")

        lines.append("# Documentation and assets")
        lines.append("docs/")
        lines.append("*.pdf")
        lines.append("*.png")
        lines.append("*.jpg")
        lines.append("*.jpeg")
        lines.append("*.gif")
        lines.append("*.svg")
        lines.append("")

        lines.append("# Third-party libraries")
        lines.append("vendor/")
        lines.append("lib/")
        lines.append("libs/")
        lines.append("")

        return "\n".join(lines)

    def _build_legacy_content(self, prompt: UniversalPrompt) -> str:
        """Build legacy .cursorrules content."""
        lines = []

        lines.append(f"# {prompt.metadata.title}")
        lines.append("")
        lines.append(prompt.metadata.description)
        lines.append("")

        # Instructions
        if prompt.instructions:
            lines.append("## Instructions")

            for category, instructions in [
                ("General", prompt.instructions.general),
                ("Code Style", prompt.instructions.code_style),
                ("Testing", prompt.instructions.testing),
            ]:
                if instructions:
                    lines.append(f"### {category}")
                    for instruction in instructions:
                        lines.append(f"- {instruction}")
                    lines.append("")

        return "\n".join(lines)
