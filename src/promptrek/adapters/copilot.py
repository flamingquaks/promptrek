"""
GitHub Copilot adapter implementation.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import click

from ..core.exceptions import DeprecationWarnings, ValidationError
from ..core.models import (
    DocumentConfig,
    Instructions,
    ProjectContext,
    PromptMetadata,
    UniversalPrompt,
    UniversalPromptV2,
    UniversalPromptV3,
)
from .base import EditorAdapter
from .mcp_mixin import MCPGenerationMixin
from .sync_mixin import SingleFileMarkdownSyncMixin


class CopilotAdapter(MCPGenerationMixin, SingleFileMarkdownSyncMixin, EditorAdapter):
    """Adapter for GitHub Copilot."""

    _description = (
        "GitHub Copilot (.github/copilot-instructions.md, "
        "path-specific instructions, agent files)"
    )
    _file_patterns = [
        ".github/copilot-instructions.md",
        ".github/instructions/*.instructions.md",
        ".github/prompts/*.prompt.md",
    ]

    def __init__(self) -> None:
        super().__init__(
            name="copilot",
            description=self._description,
            file_patterns=self._file_patterns,
        )

    def get_mcp_config_strategy(self) -> Dict[str, Any]:
        """Get MCP configuration strategy for Copilot adapter."""
        return {
            "supports_project": True,
            "project_path": ".vscode/mcp.json",
            "system_path": None,  # Copilot only supports project-level
            "requires_confirmation": False,
            "config_format": "json",
        }

    def generate(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> List[Path]:
        """Generate GitHub Copilot configuration files."""

        # V3: Always use plugin generation (handles instructions + plugins)
        if isinstance(prompt, UniversalPromptV3):
            return self._generate_plugins(
                prompt, output_dir, dry_run, verbose, variables, headless
            )

        # V2.1: Handle plugins if present
        if isinstance(prompt, UniversalPromptV2) and prompt.plugins:
            return self._generate_plugins(
                prompt, output_dir, dry_run, verbose, variables, headless
            )

        # V2: Direct markdown output
        if isinstance(prompt, UniversalPromptV2):
            return self._generate_v2(
                prompt, output_dir, dry_run, verbose, variables, headless
            )

        # V1: Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)

        # Process conditionals if supported
        conditional_content = self.process_conditionals(processed_prompt, variables)

        created_files = []

        # Generate repository-wide instructions
        copilot_file = self._generate_copilot_instructions(
            processed_prompt,
            conditional_content,
            output_dir,
            dry_run,
            verbose,
            headless,
        )
        created_files.extend(copilot_file)

        # Generate path-specific instructions
        path_files = self._generate_path_specific_instructions(
            processed_prompt, output_dir, dry_run, verbose
        )
        created_files.extend(path_files)

        # Generate experimental prompt files
        prompt_files = self._generate_prompt_files(
            processed_prompt, output_dir, dry_run, verbose
        )
        created_files.extend(prompt_files)

        return created_files

    def _generate_v2(
        self,
        prompt: Union[UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> List[Path]:
        """Generate Copilot files from v2/v3 schema."""
        github_dir = output_dir / ".github"
        output_file = github_dir / "copilot-instructions.md"

        # Apply variable substitution
        content = prompt.content
        if variables:
            for var_name, var_value in variables.items():
                placeholder = "{{{ " + var_name + " }}}"
                content = content.replace(placeholder, var_value)

        # Add headless instructions if requested
        if headless:
            lines = [
                "<!-- HEADLESS INSTRUCTIONS START -->",
                "<!-- ",
                "COPILOT HEADLESS AGENT INSTRUCTIONS:",
                "Before starting any coding tasks, run the following command to generate full instructions:",
                "`promptrek generate --editor copilot`",
                "",
                "This will regenerate the complete GitHub Copilot instructions from the source .promptrek.yaml files.",
                "-->",
                "<!-- HEADLESS INSTRUCTIONS END -->",
                "",
                content,
            ]
            content = "\n".join(lines)

        if dry_run:
            click.echo(f"  📁 Would create: {output_file}")
            if verbose:
                preview = content[:200] + "..." if len(content) > 200 else content
                click.echo(f"    {preview}")
        else:
            github_dir.mkdir(exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"✅ Generated: {output_file}")

        return [output_file]

    def _generate_plugins(
        self,
        prompt: Union[UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> List[Path]:
        """Generate Copilot files from v2.1/v3.0 schema with plugin support."""
        created_files = []

        # First, generate the regular v2/v3 markdown files
        markdown_files = self._generate_v2(
            prompt, output_dir, dry_run, verbose, variables, headless
        )
        created_files.extend(markdown_files)

        # Then, extract and handle MCP servers from either v3 top-level or v2.1 nested structure
        mcp_servers = None

        if isinstance(prompt, UniversalPromptV3):
            # V3: Check top-level field
            mcp_servers = prompt.mcp_servers
        elif isinstance(prompt, UniversalPromptV2) and prompt.plugins:
            # V2.1: Use nested plugins structure (deprecated)
            if prompt.plugins.mcp_servers:
                # Use centralized deprecation warning
                click.echo(
                    DeprecationWarnings.v3_nested_plugin_field_warning("mcp_servers")
                )
                mcp_servers = prompt.plugins.mcp_servers

        # Generate MCP config if we have MCP servers
        if mcp_servers:
            mcp_files = self._generate_mcp_config(
                mcp_servers,
                output_dir,
                dry_run,
                verbose,
                variables,
            )
            created_files.extend(mcp_files)

        return created_files

    def _generate_mcp_config(
        self,
        mcp_servers: list,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate MCP configuration for Copilot (project-only)."""
        strategy = self.get_mcp_config_strategy()
        created_files = []

        # Copilot only supports project-level
        if strategy["supports_project"] and strategy["project_path"]:
            project_config_path = output_dir / strategy["project_path"]

            # Build MCP servers config (uses standard MCP format)
            mcp_config = self.build_mcp_servers_config(
                mcp_servers, variables, format_style="standard"
            )

            # Check if config already exists
            existing_config = self.read_existing_mcp_config(project_config_path)

            if existing_config:
                # Merge with existing config
                if verbose:
                    click.echo("  ℹ️  Merging MCP servers with existing Copilot config")
                merged_config = self.merge_mcp_config(
                    existing_config, mcp_config, format_style="standard"
                )
            else:
                merged_config = mcp_config

            # Write the config
            if self.write_mcp_config_file(
                merged_config, project_config_path, dry_run, verbose
            ):
                created_files.append(project_config_path)

        return created_files

    def _generate_copilot_instructions(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        conditional_content: Optional[Dict[str, Any]],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        headless: bool = False,
    ) -> List[Path]:
        """Generate repository-wide .github/copilot-instructions.md."""
        github_dir = output_dir / ".github"
        output_file = github_dir / "copilot-instructions.md"

        # For V2/V3, use content directly
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            content = prompt.content
        elif headless:
            content = self._build_headless_content(prompt, conditional_content)
        else:
            content = self._build_repository_content(prompt, conditional_content)

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
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate path-specific .github/instructions/*.instructions.md files."""
        # V2/V3 doesn't generate path-specific files
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            return []

        instructions_dir = output_dir / ".github" / "instructions"
        created_files = []

        # Generate code style instructions for source files (V1 only)
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

    def _generate_prompt_files(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate experimental .github/prompts/*.prompt.md files."""
        # V2/V3 doesn't generate experimental prompt files
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            return []

        prompts_dir = output_dir / ".github" / "prompts"
        created_files = []

        # Generate general coding prompt (V1 only)
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

    def generate_merged(
        self,
        prompt_files: List[
            Tuple[Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3], Path]
        ],
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> List[Path]:
        """Generate merged GitHub Copilot instructions from multiple prompt files."""

        # Check if any v2/v3 files (use simple concatenation for v2/v3)
        has_v2 = any(
            isinstance(p, (UniversalPromptV2, UniversalPromptV3))
            for p, _ in prompt_files
        )

        if has_v2:
            content = self._build_merged_content_v2(prompt_files, variables, headless)
        else:
            # Build merged content for v1
            if headless:
                content = self._build_merged_headless_content(prompt_files, variables)
            else:
                content = self._build_merged_content(prompt_files, variables)

        # Determine output path
        github_dir = output_dir / ".github"
        output_file = github_dir / "copilot-instructions.md"

        if dry_run:
            click.echo(f"  📁 Would create merged: {output_file}")
            if verbose:
                click.echo("  📄 Merged content preview:")
                preview = content[:300] + "..." if len(content) > 300 else content
                click.echo(f"    {preview}")
        else:
            # Create directory and file
            github_dir.mkdir(exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            source_files = [str(pf[1]) for pf in prompt_files]
            click.echo(
                f"✅ Generated merged: {output_file} (from {len(prompt_files)} files)"
            )

        return [output_file]

    def _build_merged_content_v2(
        self,
        prompt_files: List[
            Tuple[Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3], Path]
        ],
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> str:
        """Build merged content from v2/v3 prompts (simple markdown concatenation)."""
        lines = []

        # Add headless header if requested
        if headless:
            lines.extend(
                [
                    "<!-- HEADLESS INSTRUCTIONS START -->",
                    "<!-- ",
                    "COPILOT HEADLESS AGENT INSTRUCTIONS:",
                    "Before starting any coding tasks, run the following command to generate full instructions:",
                    "`promptrek generate --editor copilot`",
                    "",
                    "This will regenerate the complete GitHub Copilot instructions from the source .promptrek.yaml files.",
                    "-->",
                    "<!-- HEADLESS INSTRUCTIONS END -->",
                    "",
                ]
            )

        # Add header
        lines.append("# GitHub Copilot Instructions")
        lines.append("")
        lines.append(f"Merged from {len(prompt_files)} configuration file(s)")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Concatenate all content
        for i, (prompt, source_file) in enumerate(prompt_files, 1):
            if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
                content = prompt.content
            else:
                # Convert v1 to markdown on the fly
                content = f"# {prompt.metadata.title}\n\n{prompt.metadata.description}"

            # Apply variable substitution
            if variables:
                for var_name, var_value in variables.items():
                    placeholder = "{{{ " + var_name + " }}}"
                    content = content.replace(placeholder, var_value)

            lines.append(content)

            if i < len(prompt_files):
                lines.append("")
                lines.append("---")
                lines.append("")

        return "\n".join(lines)

    def _build_merged_content(
        self,
        prompt_files: Sequence[
            Tuple[Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3], Path]
        ],
        variables: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build merged GitHub Copilot instructions from multiple prompt files."""
        lines = []

        # Header with summary
        lines.append("# GitHub Copilot Instructions")
        lines.append("")
        lines.append(
            f"This document contains merged GitHub Copilot instructions from {len(prompt_files)} configuration files."
        )
        lines.append("")

        # Configuration files list
        lines.append("## Configuration Sources")
        for i, (prompt, source_file) in enumerate(prompt_files, 1):
            lines.append(
                f"{i}. **{prompt.metadata.title}** (`{source_file.name}`) - {prompt.metadata.description}"
            )
        lines.append("")

        # Process each file
        for i, (prompt, source_file) in enumerate(prompt_files, 1):
            # Apply variable substitution if supported
            processed_prompt = self.substitute_variables(prompt, variables)

            lines.append(f"## {i}. {processed_prompt.metadata.title}")
            lines.append("")
            lines.append(f"*Source: `{source_file.name}`*")
            lines.append("")
            lines.append(processed_prompt.metadata.description)
            lines.append("")

            # For V2/V3, use content directly
            if isinstance(processed_prompt, (UniversalPromptV2, UniversalPromptV3)):
                lines.append(processed_prompt.content)
                lines.append("")
                continue

            # Instructions (V1 only)
            if processed_prompt.instructions:
                lines.append("### Instructions")
                # Handle all instruction categories dynamically
                instruction_data = processed_prompt.instructions.model_dump()
                for category, instructions in instruction_data.items():
                    if instructions:  # Only include non-empty categories
                        category_title = category.replace("_", " ").title()
                        lines.append(f"#### {category_title}")
                        for instruction in instructions:
                            lines.append(f"- {instruction}")
                        lines.append("")

            # Add a separator between files (except for the last one)
            if i < len(prompt_files):
                lines.append("---")
                lines.append("")

        return "\n".join(lines)

    def _build_merged_headless_content(
        self,
        prompt_files: Sequence[
            Tuple[Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3], Path]
        ],
        variables: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build merged headless content with embedded generation instructions."""
        lines = []

        # Headless instructions block
        lines.append("<!-- HEADLESS INSTRUCTIONS START -->")
        lines.append("<!-- ")
        lines.append("COPILOT HEADLESS AGENT INSTRUCTIONS:")
        lines.append(
            "Before starting any coding tasks, run the following command to generate full instructions:"
        )
        lines.append("`promptrek generate --editor copilot`")
        lines.append("")
        lines.append(
            "This will regenerate the complete GitHub Copilot instructions from the source .promptrek.yaml files."
        )
        lines.append(
            "The generated content will replace everything between HEADLESS INSTRUCTIONS END and the end of this file."
        )
        lines.append("-->")
        lines.append("<!-- HEADLESS INSTRUCTIONS END -->")
        lines.append("")

        # Full merged content
        full_content = self._build_merged_content(prompt_files, variables)
        lines.append(full_content)

        return "\n".join(lines)

    def parse_files(
        self, source_dir: Path
    ) -> Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]:
        """
        Parse GitHub Copilot files back into a UniversalPromptV2.

        Uses v2 format for lossless sync.

        Args:
            source_dir: Directory containing Copilot configuration files

        Returns:
            UniversalPromptV2 object parsed from Copilot files
        """
        file_path = ".github/copilot-instructions.md"
        # Use v2 sync for lossless roundtrip
        return self.parse_single_markdown_file_v2(
            source_dir=source_dir,
            file_path=file_path,
            editor_name="GitHub Copilot",
        )

    def _parse_copilot_instructions_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse the main copilot-instructions.md file."""
        result: Dict[str, Any] = {}

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Skip headless instructions block if present
        content = self._strip_headless_instructions(content)

        # Parse metadata from header
        lines = content.split("\n")
        title = None
        description = None

        # Extract title (first # header)
        for line in lines:
            line = line.strip()
            if line.startswith("# ") and not title:
                title = line[2:].strip()
                break

        # Find description (text after title, before first ##)
        in_description = False
        desc_lines = []
        for line in lines:
            line = line.strip()
            if line.startswith("# ") and title:
                in_description = True
                continue
            elif in_description:
                if line.startswith("##"):
                    break
                elif line:
                    desc_lines.append(line)

        if desc_lines:
            description = " ".join(desc_lines)

        # Update metadata
        if title or description:
            result["metadata"] = PromptMetadata(
                title=title or "GitHub Copilot Configuration",
                description=description
                or "Configuration parsed from GitHub Copilot files",
            )

        # Parse instructions by section
        instructions_dict: Dict[str, List[str]] = {}
        current_section = None
        current_items: List[str] = []

        for line in lines:
            line = line.strip()

            # Section headers
            if line.startswith("## "):
                # Save previous section
                if current_section and current_items:
                    instructions_dict[current_section] = current_items

                # Start new section
                section_name = line[3:].strip()
                current_section = self._normalize_section_name(section_name)
                current_items = []

            # Bullet points
            elif line.startswith("- ") and current_section is not None:
                instruction = line[2:].strip()
                if instruction and instruction not in current_items:
                    current_items.append(instruction)

        # Save final section
        if current_section and current_items:
            instructions_dict[current_section] = current_items

        # Create Instructions object
        if instructions_dict:
            # Valid instruction categories from the Instructions model
            valid_categories = {
                "general",
                "code_style",
                "architecture",
                "testing",
                "security",
                "performance",
            }
            filtered_dict = {
                k: v
                for k, v in instructions_dict.items()
                if k in valid_categories and v
            }
            result["instructions"] = Instructions(**filtered_dict)

        # Extract project context
        context_info = self._extract_project_context(content)
        if context_info:
            result["context"] = context_info

        return result

    def _parse_instructions_directory(self, instructions_dir: Path) -> Instructions:
        """Parse .github/instructions/*.instructions.md files."""
        instructions_dict: Dict[str, List[str]] = {}

        for file_path in instructions_dir.glob("*.instructions.md"):
            category = self._filename_to_category(file_path.stem)
            parsed_instructions = self._parse_instruction_file(file_path)
            if parsed_instructions:
                instructions_dict[category] = parsed_instructions

        return Instructions(**instructions_dict)

    def _parse_prompts_directory(self, prompts_dir: Path) -> Instructions:
        """Parse .github/prompts/*.prompt.md files."""
        instructions_dict: Dict[str, List[str]] = {}

        for file_path in prompts_dir.glob("*.prompt.md"):
            # Prompts usually contain general guidelines
            parsed_prompts = self._parse_prompt_file(file_path)
            if parsed_prompts:
                # Most prompts go to general category
                if "general" not in instructions_dict:
                    instructions_dict["general"] = []
                instructions_dict["general"].extend(parsed_prompts)

        return Instructions(**instructions_dict)

    def _parse_instruction_file(self, file_path: Path) -> List[str]:
        """Parse individual .instructions.md file."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Skip YAML frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2].strip()

        instructions = []
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("- "):
                instruction = line[2:].strip()
                if instruction:
                    instructions.append(instruction)

        return instructions

    def _parse_prompt_file(self, file_path: Path) -> List[str]:
        """Parse individual .prompt.md file."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        instructions = []
        in_guidelines = False

        for line in content.split("\n"):
            line = line.strip()

            # Look for guideline sections
            if "guideline" in line.lower() or "instruction" in line.lower():
                in_guidelines = True
                continue
            elif line.startswith("#"):
                in_guidelines = False

            if in_guidelines and line.startswith("- "):
                instruction = line[2:].strip()
                if instruction:
                    instructions.append(instruction)

        return instructions

    def _strip_headless_instructions(self, content: str) -> str:
        """Remove headless instruction block from content."""
        start_marker = "<!-- HEADLESS INSTRUCTIONS START -->"
        end_marker = "<!-- HEADLESS INSTRUCTIONS END -->"

        start_pos = content.find(start_marker)
        if start_pos == -1:
            return content

        end_pos = content.find(end_marker)
        if end_pos == -1:
            return content

        # Remove the entire headless block
        return content[:start_pos] + content[end_pos + len(end_marker) :].lstrip()

    def _normalize_section_name(self, section_name: str) -> Optional[str]:
        """Normalize section names to instruction categories."""
        section_lower = section_name.lower()

        # Skip non-instruction sections
        skip_sections = {
            "project information",
            "project info",
            "examples",
            "about",
            "overview",
        }
        if section_lower in skip_sections:
            return None  # Skip this section

        mapping = {
            "general instructions": "general",
            "general guidelines": "general",
            "general": "general",
            "code style guidelines": "code_style",
            "code style": "code_style",
            "testing guidelines": "testing",
            "testing": "testing",
            "architecture": "architecture",
            "architecture guidelines": "architecture",
            "security": "security",
            "security guidelines": "security",
            "performance": "performance",
            "performance guidelines": "performance",
        }
        return mapping.get(section_lower, "general")

    def _filename_to_category(self, filename: str) -> str:
        """Convert filename to instruction category."""
        # Remove .instructions suffix if present
        if filename.endswith(".instructions"):
            filename = filename[:-12]

        mapping = {
            "code-style": "code_style",
            "testing": "testing",
            "architecture": "architecture",
            "security": "security",
            "performance": "performance",
        }
        return mapping.get(filename, "general")

    def _extract_project_context(self, content: str) -> Optional[ProjectContext]:
        """Extract project context information from content."""
        context_data: Dict[str, Any] = {}

        # Look for technology mentions
        tech_patterns = [
            r"Technologies?:\s*([^\n]+)",
            r"Tech stack:\s*([^\n]+)",
            r"Using\s+([^,\n]+(?:,\s*[^,\n]+)*)",
        ]

        technologies = []
        for pattern in tech_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Split on commas and clean up
                techs = [t.strip() for t in match.split(",")]
                technologies.extend([t for t in techs if t and len(t) < 30])

        if technologies:
            context_data["technologies"] = list(set(technologies))

        # Look for project type
        type_patterns = [
            r"Type:\s*([^\n]+)",
            r"Project\s+type:\s*([^\n]+)",
        ]

        for pattern in type_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                context_data["project_type"] = match.group(1).strip()
                break

        return ProjectContext(**context_data) if context_data else None

    def _merge_instructions(
        self, base: Instructions, additional: Instructions
    ) -> Instructions:
        """Merge two Instructions objects without duplication."""
        base_dict = base.model_dump(exclude_none=True)
        additional_dict = additional.model_dump(exclude_none=True)

        # Merge each category
        for category, new_instructions in additional_dict.items():
            if isinstance(new_instructions, list) and new_instructions:
                if category not in base_dict:
                    base_dict[category] = []
                elif not isinstance(base_dict[category], list):
                    base_dict[category] = []

                # Add new instructions, avoiding duplicates
                existing_set = set(base_dict[category])
                for instruction in new_instructions:
                    if instruction not in existing_set:
                        base_dict[category].append(instruction)

        return Instructions(**base_dict)

    def validate(
        self, prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]
    ) -> List[ValidationError]:
        """Validate prompt for Copilot."""
        errors = []

        # V2/V3 validation: check content exists
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            if not prompt.content or not prompt.content.strip():
                errors.append(
                    ValidationError(
                        field="content",
                        message="GitHub Copilot requires content",
                        severity="error",
                    )
                )
            return errors

        # V1 validation: Copilot works best with clear instructions
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

    def _build_repository_content(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]] = None,
    ) -> str:
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

        # Instructions (including conditional)
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
            lines.append("## General Instructions")
            for instruction in all_instructions:
                lines.append(f"- {instruction}")
            lines.append("")

            if prompt.instructions and prompt.instructions.code_style:
                lines.append("## Code Style Guidelines")
                for guideline in prompt.instructions.code_style:
                    lines.append(f"- {guideline}")
                lines.append("")

            if prompt.instructions and prompt.instructions.testing:
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

    def _build_headless_content(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build headless agent content with embedded generation instructions."""
        lines = []

        # Headless instructions block
        lines.append("<!-- HEADLESS INSTRUCTIONS START -->")
        lines.append("<!-- ")
        lines.append("COPILOT HEADLESS AGENT INSTRUCTIONS:")
        lines.append(
            "Before starting any coding tasks, run the following command to generate full instructions:"
        )
        lines.append("`promptrek generate --editor copilot`")
        lines.append("")
        lines.append(
            "This will regenerate the complete GitHub Copilot instructions from the source .promptrek.yaml files."
        )
        lines.append(
            "The generated content will replace everything between HEADLESS INSTRUCTIONS END and the end of this file."
        )
        lines.append("-->")
        lines.append("<!-- HEADLESS INSTRUCTIONS END -->")
        lines.append("")

        # Full generated content
        full_content = self._build_repository_content(prompt, conditional_content)
        lines.append(full_content)

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
            "- **Function Creation:** Generate well-documented functions "
            "with proper typing"
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
