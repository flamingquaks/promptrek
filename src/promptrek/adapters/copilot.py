"""
GitHub Copilot adapter implementation.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from ..core.exceptions import ValidationError
from ..core.models import UniversalPrompt
from .base import EditorAdapter


class CopilotAdapter(EditorAdapter):
    """Adapter for GitHub Copilot."""

    _description = "GitHub Copilot (.github/copilot-instructions.md, path-specific instructions, agent files)"
    _file_patterns = [
        ".github/copilot-instructions.md",
        ".github/instructions/*.instructions.md",
        ".github/prompts/*.prompt.md",
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
    ]

    def __init__(self):
        super().__init__(
            name="copilot",
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
        """Generate GitHub Copilot configuration files."""

        # Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)

        created_files = []

        # Generate repository-wide instructions
        copilot_file = self._generate_copilot_instructions(
            processed_prompt, output_dir, dry_run, verbose
        )
        created_files.extend(copilot_file)

        # Generate path-specific instructions
        path_files = self._generate_path_specific_instructions(
            processed_prompt, output_dir, dry_run, verbose
        )
        created_files.extend(path_files)

        # Generate agent instructions
        agent_files = self._generate_agent_instructions(
            processed_prompt, output_dir, dry_run, verbose
        )
        created_files.extend(agent_files)

        # Generate experimental prompt files
        prompt_files = self._generate_prompt_files(
            processed_prompt, output_dir, dry_run, verbose
        )
        created_files.extend(prompt_files)

        return created_files

    def _generate_copilot_instructions(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate repository-wide .github/copilot-instructions.md."""
        github_dir = output_dir / ".github"
        output_file = github_dir / "copilot-instructions.md"
        content = self._build_repository_content(prompt)

        if dry_run:
            click.echo(f"  📁 Would create: {output_file}")
            if verbose:
                click.echo("  📄 Repository instructions preview:")
                preview = content[:200] + "..." if len(content) > 200 else content
                click.echo(f"    {preview}")
        else:
            github_dir.mkdir(exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"✅ Generated: {output_file}")
            return [output_file]

        return []

    def _generate_path_specific_instructions(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate path-specific .github/instructions/*.instructions.md files."""
        instructions_dir = output_dir / ".github" / "instructions"
        created_files = []

        # Generate code style instructions for source files
        if prompt.instructions and prompt.instructions.code_style:
            code_file = instructions_dir / "code-style.instructions.md"
            code_content = self._build_path_specific_content(
                "Code Style Guidelines",
                prompt.instructions.code_style,
                "**/*.{ts,tsx,js,jsx,py,java,go,rs,cpp,c,h}",
            )

            if dry_run:
                click.echo(f"  📁 Would create: {code_file}")
                if verbose:
                    preview = (
                        code_content[:200] + "..."
                        if len(code_content) > 200
                        else code_content
                    )
                    click.echo(f"    {preview}")
            else:
                instructions_dir.mkdir(parents=True, exist_ok=True)
                with open(code_file, "w", encoding="utf-8") as f:
                    f.write(code_content)
                click.echo(f"✅ Generated: {code_file}")
                created_files.append(code_file)

        # Generate testing instructions for test files
        if prompt.instructions and prompt.instructions.testing:
            test_file = instructions_dir / "testing.instructions.md"
            test_content = self._build_path_specific_content(
                "Testing Guidelines",
                prompt.instructions.testing,
                "**/*.{test,spec}.{ts,tsx,js,jsx,py}",
            )

            if dry_run:
                click.echo(f"  📁 Would create: {test_file}")
                if verbose:
                    preview = (
                        test_content[:200] + "..."
                        if len(test_content) > 200
                        else test_content
                    )
                    click.echo(f"    {preview}")
            else:
                instructions_dir.mkdir(parents=True, exist_ok=True)
                with open(test_file, "w", encoding="utf-8") as f:
                    f.write(test_content)
                click.echo(f"✅ Generated: {test_file}")
                created_files.append(test_file)

        # Generate technology-specific instructions
        if prompt.context and prompt.context.technologies:
            for tech in prompt.context.technologies[:2]:  # Limit to 2 main technologies
                tech_file = instructions_dir / f"{tech.lower()}.instructions.md"
                tech_content = self._build_tech_specific_content(tech, prompt)

                if dry_run:
                    click.echo(f"  📁 Would create: {tech_file}")
                    if verbose:
                        preview = (
                            tech_content[:200] + "..."
                            if len(tech_content) > 200
                            else tech_content
                        )
                        click.echo(f"    {preview}")
                else:
                    instructions_dir.mkdir(parents=True, exist_ok=True)
                    with open(tech_file, "w", encoding="utf-8") as f:
                        f.write(tech_content)
                    click.echo(f"✅ Generated: {tech_file}")
                    created_files.append(tech_file)

        return created_files

    def _generate_agent_instructions(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate agent instruction files (AGENTS.md, CLAUDE.md, GEMINI.md)."""
        created_files = []

        # Generate general AGENTS.md
        agents_file = output_dir / "AGENTS.md"
        agents_content = self._build_agents_content(prompt)

        if dry_run:
            click.echo(f"  📁 Would create: {agents_file}")
            if verbose:
                preview = (
                    agents_content[:200] + "..."
                    if len(agents_content) > 200
                    else agents_content
                )
                click.echo(f"    {preview}")
        else:
            with open(agents_file, "w", encoding="utf-8") as f:
                f.write(agents_content)
            click.echo(f"✅ Generated: {agents_file}")
            created_files.append(agents_file)

        # Generate CLAUDE.md for Claude-specific instructions
        claude_file = output_dir / "CLAUDE.md"
        claude_content = self._build_claude_content(prompt)

        if dry_run:
            click.echo(f"  📁 Would create: {claude_file}")
            if verbose:
                preview = (
                    claude_content[:200] + "..."
                    if len(claude_content) > 200
                    else claude_content
                )
                click.echo(f"    {preview}")
        else:
            with open(claude_file, "w", encoding="utf-8") as f:
                f.write(claude_content)
            click.echo(f"✅ Generated: {claude_file}")
            created_files.append(claude_file)

        return created_files

    def _generate_prompt_files(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate experimental .github/prompts/*.prompt.md files."""
        prompts_dir = output_dir / ".github" / "prompts"
        created_files = []

        # Generate general coding prompt
        coding_prompt_file = prompts_dir / "coding.prompt.md"
        coding_prompt_content = self._build_coding_prompt_content(prompt)

        if dry_run:
            click.echo(f"  📁 Would create: {coding_prompt_file} (experimental)")
            if verbose:
                preview = (
                    coding_prompt_content[:200] + "..."
                    if len(coding_prompt_content) > 200
                    else coding_prompt_content
                )
                click.echo(f"    {preview}")
        else:
            prompts_dir.mkdir(parents=True, exist_ok=True)
            with open(coding_prompt_file, "w", encoding="utf-8") as f:
                f.write(coding_prompt_content)
            click.echo(f"✅ Generated: {coding_prompt_file} (experimental)")
            created_files.append(coding_prompt_file)

        return created_files

    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """Validate prompt for Copilot."""
        errors = []

        # Copilot works best with clear instructions
        if not prompt.instructions or not prompt.instructions.general:
            errors.append(
                ValidationError(
                    field="instructions.general",
                    message="GitHub Copilot works best with general instructions",
                )
            )

        return errors

    def supports_variables(self) -> bool:
        """Copilot supports variable substitution through templating."""
        return True

    def supports_conditionals(self) -> bool:
        """Copilot supports conditional instructions."""
        return True

    def _build_repository_content(self, prompt: UniversalPrompt) -> str:
        """Build repository-wide GitHub Copilot instructions content."""
        lines = []

        # Header
        lines.append(f"# {prompt.metadata.title}")
        lines.append("")
        lines.append(prompt.metadata.description)
        lines.append("")

        # Project Information
        if prompt.context:
            lines.append("## Project Information")
            if prompt.context.project_type:
                lines.append(f"- Type: {prompt.context.project_type}")
            if prompt.context.technologies:
                lines.append(
                    f"- Technologies: {', '.join(prompt.context.technologies)}"
                )
            if prompt.context.description:
                lines.append(f"- Description: {prompt.context.description}")
            lines.append("")

        # Instructions
        if prompt.instructions:
            if prompt.instructions.general:
                lines.append("## General Instructions")
                for instruction in prompt.instructions.general:
                    lines.append(f"- {instruction}")
                lines.append("")

            if prompt.instructions.code_style:
                lines.append("## Code Style Guidelines")
                for guideline in prompt.instructions.code_style:
                    lines.append(f"- {guideline}")
                lines.append("")

            if prompt.instructions.testing:
                lines.append("## Testing Guidelines")
                for guideline in prompt.instructions.testing:
                    lines.append(f"- {guideline}")
                lines.append("")

        # Examples
        if prompt.examples:
            lines.append("## Examples")
            for name, example in prompt.examples.items():
                lines.append(f"### {name.title()}")
                lines.append(example)
                lines.append("")

        return "\n".join(lines)

    def _build_path_specific_content(
        self, title: str, instructions: List[str], apply_to: str
    ) -> str:
        """Build path-specific instruction content with frontmatter."""
        lines = []

        # YAML frontmatter
        lines.append("---")
        lines.append(f'applyTo: "{apply_to}"')
        lines.append("---")
        lines.append("")

        # Content
        lines.append(f"# {title}")
        lines.append("")

        for instruction in instructions:
            lines.append(f"- {instruction}")

        return "\n".join(lines)

    def _build_tech_specific_content(self, tech: str, prompt: UniversalPrompt) -> str:
        """Build technology-specific instruction content."""
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

        pattern = tech_patterns.get(tech.lower(), f"**/*.{tech.lower()}")

        # YAML frontmatter
        lines.append("---")
        lines.append(f'applyTo: "{pattern}"')
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
                "Implement proper error handling",
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

    def _build_agents_content(self, prompt: UniversalPrompt) -> str:
        """Build general agent instructions content."""
        lines = []

        lines.append(f"# {prompt.metadata.title} - Agent Instructions")
        lines.append("")
        lines.append(prompt.metadata.description)
        lines.append("")

        # Project Context
        if prompt.context:
            lines.append("## Project Context")
            if prompt.context.project_type:
                lines.append(f"**Project Type:** {prompt.context.project_type}")
            if prompt.context.technologies:
                lines.append(
                    f"**Technologies:** {', '.join(prompt.context.technologies)}"
                )
            if prompt.context.description:
                lines.append("")
                lines.append("**Project Description:**")
                lines.append(prompt.context.description)
            lines.append("")

        # Instructions for AI agents
        lines.append("## AI Agent Guidelines")
        lines.append("")

        if prompt.instructions:
            if prompt.instructions.general:
                lines.append("### General Instructions")
                for instruction in prompt.instructions.general:
                    lines.append(f"- {instruction}")
                lines.append("")

            if prompt.instructions.code_style:
                lines.append("### Code Style Requirements")
                for guideline in prompt.instructions.code_style:
                    lines.append(f"- {guideline}")
                lines.append("")

            if prompt.instructions.testing:
                lines.append("### Testing Requirements")
                for guideline in prompt.instructions.testing:
                    lines.append(f"- {guideline}")
                lines.append("")

        # AI-specific guidance
        lines.append("### AI Assistance Guidelines")
        lines.append("- Provide clear, well-documented code solutions")
        lines.append("- Explain complex logic and design decisions")
        lines.append("- Suggest best practices and improvements")
        lines.append("- Consider security and performance implications")
        if prompt.context and prompt.context.technologies:
            tech_list = ", ".join(prompt.context.technologies)
            lines.append(f"- Follow {tech_list} conventions and idioms")

        return "\n".join(lines)

    def _build_claude_content(self, prompt: UniversalPrompt) -> str:
        """Build Claude-specific instruction content."""
        lines = []

        lines.append(f"# {prompt.metadata.title} - Claude Instructions")
        lines.append("")
        lines.append(f"Claude-specific instructions for: {prompt.metadata.description}")
        lines.append("")

        # Project Context
        if prompt.context:
            lines.append("## Project Context")
            if prompt.context.project_type:
                lines.append(f"- **Project Type:** {prompt.context.project_type}")
            if prompt.context.technologies:
                lines.append(
                    f"- **Technologies:** {', '.join(prompt.context.technologies)}"
                )
            lines.append("")

        # Claude-specific instructions
        lines.append("## Instructions for Claude")
        lines.append("")

        if prompt.instructions:
            if prompt.instructions.general:
                lines.append("### General Guidelines")
                for instruction in prompt.instructions.general:
                    lines.append(f"- {instruction}")
                lines.append("")

            if prompt.instructions.code_style:
                lines.append("### Code Style Guidelines")
                for guideline in prompt.instructions.code_style:
                    lines.append(f"- {guideline}")
                lines.append("")

        # Claude-specific guidance
        lines.append("### Claude-Specific Guidelines")
        lines.append("- Provide step-by-step reasoning for complex problems")
        lines.append("- Suggest multiple approaches when appropriate")
        lines.append("- Include relevant documentation references")
        lines.append("- Explain trade-offs and considerations")
        lines.append("- Be thorough in code reviews and suggestions")

        return "\n".join(lines)

    def _build_coding_prompt_content(self, prompt: UniversalPrompt) -> str:
        """Build experimental coding prompt content for VS Code."""
        lines = []

        lines.append(f"# {prompt.metadata.title} - Coding Prompts")
        lines.append("")
        lines.append("## Project Overview")
        lines.append(prompt.metadata.description)
        lines.append("")

        # Coding prompts section
        lines.append("## Coding Assistance Prompts")
        lines.append("")

        if prompt.instructions and prompt.instructions.general:
            lines.append("### Code Generation Guidelines")
            for instruction in prompt.instructions.general:
                lines.append(f"- {instruction}")
            lines.append("")

        if prompt.instructions and prompt.instructions.code_style:
            lines.append("### Style Guidelines")
            for guideline in prompt.instructions.code_style:
                lines.append(f"- {guideline}")
            lines.append("")

        # Technology-specific prompts
        if prompt.context and prompt.context.technologies:
            lines.append("### Technology-Specific Guidance")
            for tech in prompt.context.technologies:
                lines.append(
                    f"- **{tech}:** Follow {tech} best practices and conventions"
                )
            lines.append("")

        # Common prompts
        lines.append("### Common Coding Tasks")
        lines.append(
            "- **Function Creation:** Generate well-documented functions with proper typing"
        )
        lines.append(
            "- **Code Review:** Analyze code for bugs, performance, and maintainability"
        )
        lines.append(
            "- **Refactoring:** Suggest improvements while maintaining functionality"
        )
        lines.append("- **Testing:** Generate appropriate unit tests and test cases")
        lines.append("")

        return "\n".join(lines)
