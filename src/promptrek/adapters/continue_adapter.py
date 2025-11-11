"""
Continue editor adapter implementation.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import click
import yaml

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
from .spec_mixin import SpecInclusionMixin


class ContinueAdapter(MCPGenerationMixin, SpecInclusionMixin, EditorAdapter):
    """Adapter for Continue editor."""

    _description = "Continue (.continue/rules/)"
    _file_patterns = [".continue/rules/*.md"]

    def __init__(self) -> None:
        super().__init__(
            name="continue",
            description=self._description,
            file_patterns=self._file_patterns,
        )

    def get_mcp_config_strategy(self) -> Dict[str, Any]:
        """Get MCP configuration strategy for Continue adapter."""
        return {
            "supports_project": True,
            "project_path": ".continue/config.json",
            "system_path": str(Path.home() / ".continue" / "config.json"),
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
        """Generate Continue configuration files."""

        # V3: Always use plugin generation (handles markdown + plugins)
        if isinstance(prompt, UniversalPromptV3):
            return self._generate_plugins(
                prompt, output_dir, dry_run, verbose, variables
            )

        # V2.1: Handle plugins if present
        if isinstance(prompt, UniversalPromptV2) and prompt.plugins:
            return self._generate_plugins(
                prompt, output_dir, dry_run, verbose, variables
            )

        # V2: Use documents field for multi-file generation (no plugins)
        if isinstance(prompt, UniversalPromptV2):
            return self._generate_v2(prompt, output_dir, dry_run, verbose, variables)

        # V1: Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)
        assert isinstance(
            processed_prompt, UniversalPrompt
        ), "V1 path should have UniversalPrompt"

        # Process conditionals if supported
        conditional_content = self.process_conditionals(processed_prompt, variables)

        # Generate rules directory system
        rules_files = self._generate_rules_system(
            processed_prompt, conditional_content, output_dir, dry_run, verbose
        )

        return rules_files

    def _generate_v2(
        self,
        prompt: Union[UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate Continue files from v2/v3 schema."""
        rules_dir = output_dir / ".continue" / "rules"
        created_files = []

        # If documents field is present, generate separate files
        if prompt.documents:
            for doc in prompt.documents:
                # Build frontmatter with metadata-driven defaults
                # Convert kebab-case and snake_case to Title Case for human-readable name
                doc_name_display = re.sub(r"[-_]", " ", doc.name).title()
                doc_description = (
                    doc.description
                )  # Use explicit description if provided
                doc_always_apply = (
                    doc.always_apply if doc.always_apply is not None else False
                )
                doc_globs = doc.file_globs  # Use explicit file_globs if provided

                doc_frontmatter = self._build_continue_frontmatter(
                    name=doc_name_display,  # Human-readable title case
                    description=doc_description,
                    globs=doc_globs,
                    always_apply=doc_always_apply,
                )

                doc_content = self._build_md_file_with_frontmatter(
                    frontmatter=doc_frontmatter,
                    content=doc.content,
                    variables=variables,
                )

                # Generate filename from document name
                filename = (
                    f"{doc.name}.md" if not doc.name.endswith(".md") else doc.name
                )
                output_file = rules_dir / filename

                if dry_run:
                    click.echo(f"  📁 Would create: {output_file}")
                    if verbose:
                        preview = (
                            doc_content[:200] + "..."
                            if len(doc_content) > 200
                            else doc_content
                        )
                        click.echo(f"    {preview}")
                    created_files.append(output_file)
                else:
                    rules_dir.mkdir(parents=True, exist_ok=True)
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(doc_content)
                    click.echo(f"✅ Generated: {output_file}")
                    created_files.append(output_file)
        else:
            # No documents, use main content as general rules
            main_name = "General Rules"
            main_description = prompt.content_description or "General coding guidelines"
            main_always_apply = (
                prompt.content_always_apply
                if prompt.content_always_apply is not None
                else True  # Default to always apply for main content
            )

            main_frontmatter = self._build_continue_frontmatter(
                name=main_name,
                description=main_description,
                always_apply=main_always_apply,
            )

            main_content = self._build_md_file_with_frontmatter(
                frontmatter=main_frontmatter,
                content=prompt.content,
                variables=variables,
            )

            output_file = rules_dir / "general.md"

            if dry_run:
                click.echo(f"  📁 Would create: {output_file}")
                if verbose:
                    preview = (
                        main_content[:200] + "..."
                        if len(main_content) > 200
                        else main_content
                    )
                    click.echo(f"    {preview}")
                created_files.append(output_file)
            else:
                rules_dir.mkdir(parents=True, exist_ok=True)
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(main_content)
                click.echo(f"✅ Generated: {output_file}")
                created_files.append(output_file)

        # Add spec documents if v3.1.0+ and enabled
        if self.should_include_specs(prompt):
            spec_docs = self.get_spec_documents(output_dir)
            for spec_doc in spec_docs:
                filename, spec_content = self.format_spec_as_document_frontmatter(
                    spec_doc
                )
                spec_file = rules_dir / filename

                if dry_run:
                    click.echo(f"  📁 Would create: {spec_file} (spec)")
                    if verbose:
                        preview = (
                            spec_content[:200] + "..."
                            if len(spec_content) > 200
                            else spec_content
                        )
                        click.echo(f"    {preview}")
                    created_files.append(spec_file)
                else:
                    rules_dir.mkdir(parents=True, exist_ok=True)
                    with open(spec_file, "w", encoding="utf-8") as f:
                        f.write(spec_content)
                    click.echo(f"✅ Generated: {spec_file} (spec)")
                    created_files.append(spec_file)

        return created_files

    def _generate_plugins(
        self,
        prompt: Union[UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate Continue files from v2.1/v3.0 schema with plugin support."""
        created_files = []

        # First, generate the regular v2/v3 markdown files
        markdown_files = self._generate_v2(
            prompt, output_dir, dry_run, verbose, variables
        )
        created_files.extend(markdown_files)

        # Then, handle all plugins from either v3 top-level or v2.1 nested structure
        # Extract plugin data
        mcp_servers = None
        commands = None

        if isinstance(prompt, UniversalPromptV3):
            # V3: Check top-level fields
            mcp_servers = prompt.mcp_servers
            commands = prompt.commands
        elif isinstance(prompt, UniversalPromptV2) and prompt.plugins:
            # V2.1: Use nested plugins structure (deprecated)
            if prompt.plugins.mcp_servers:
                click.echo(
                    DeprecationWarnings.v3_nested_plugin_field_warning("mcp_servers")
                )
                mcp_servers = prompt.plugins.mcp_servers
            if prompt.plugins.commands:
                click.echo(
                    DeprecationWarnings.v3_nested_plugin_field_warning("commands")
                )
                commands = prompt.plugins.commands

        # Generate plugin config if we have any plugins
        if mcp_servers or commands:
            plugin_files = self._generate_all_plugins_config(
                mcp_servers,
                commands,
                output_dir,
                dry_run,
                verbose,
                variables,
            )
            created_files.extend(plugin_files)

        return created_files

    def _generate_all_plugins_config(
        self,
        mcp_servers: Optional[List[Any]],
        commands: Optional[List[Any]],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate modular plugin configuration for Continue (individual files per server/command)."""
        created_files = []

        # Generate individual MCP server YAML files
        if mcp_servers:
            mcp_files = self._generate_individual_mcp_files(
                mcp_servers, output_dir, dry_run, verbose, variables
            )
            created_files.extend(mcp_files)

        # Generate individual prompt markdown files
        if commands:
            prompt_files = self._generate_individual_prompt_files(
                commands, output_dir, dry_run, verbose, variables
            )
            created_files.extend(prompt_files)

        # Generate config.yaml if we have any plugins
        if mcp_servers or commands:
            config_file = self._generate_config_yaml(
                mcp_servers, commands, output_dir, dry_run, verbose, variables
            )
            if config_file:
                created_files.append(config_file)

        return created_files

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize a string to be safe for use as a filename.

        Args:
            name: The name to sanitize

        Returns:
            A sanitized filename containing only alphanumeric characters, hyphens, and underscores
        """
        # Replace any character that's not alphanumeric, hyphen, or underscore with hyphen
        sanitized = re.sub(r"[^a-zA-Z0-9_-]", "-", name)
        # Remove leading/trailing hyphens and collapse multiple hyphens
        sanitized = re.sub(r"-+", "-", sanitized).strip("-")
        # Ensure we have at least some valid characters
        if not sanitized:
            sanitized = "unnamed"
        return sanitized

    def _format_server_name(self, name: str) -> str:
        """Format a server name for display, preserving known acronyms.

        Args:
            name: The server name (e.g., "github", "filesystem")

        Returns:
            A formatted display name (e.g., "GitHub", "Filesystem")
        """
        # Special case mappings for known acronyms and proper names
        special_cases = {
            "github": "GitHub",
            "gitlab": "GitLab",
            "npm": "NPM",
            "aws": "AWS",
            "api": "API",
            "http": "HTTP",
            "https": "HTTPS",
            "ssh": "SSH",
            "sql": "SQL",
            "mysql": "MySQL",
            "postgresql": "PostgreSQL",
            "mongodb": "MongoDB",
        }

        # Check if the name matches a special case
        lower_name = name.lower()
        if lower_name in special_cases:
            return special_cases[lower_name]

        # Otherwise, use title case
        return name.replace("-", " ").replace("_", " ").title()

    def _generate_individual_mcp_files(
        self,
        mcp_servers: List[Any],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate individual YAML files for each MCP server in .continue/mcpServers/."""
        mcp_dir = output_dir / ".continue" / "mcpServers"
        created_files = []

        for server in mcp_servers:
            # Apply variable substitution to env vars
            env_vars = {}
            if server.env:
                for key, value in server.env.items():
                    substituted_value = value
                    if variables:
                        for var_name, var_value in variables.items():
                            placeholder = "{{{ " + var_name + " }}}"
                            substituted_value = substituted_value.replace(
                                placeholder, var_value
                            )
                    env_vars[key] = substituted_value

            # Build server config
            server_config: Dict[str, Any] = {
                "name": server.name,
                "command": server.command,
                "args": server.args,
            }

            if env_vars:
                server_config["env"] = env_vars

            # Build Continue-specific YAML format
            yaml_content = {
                "name": self._format_server_name(server.name) + " MCP Server",
                "version": "0.0.1",
                "schema": "v1",
                "mcpServers": [server_config],
            }

            # Write YAML file with sanitized filename
            safe_filename = self._sanitize_filename(server.name)
            yaml_file = mcp_dir / f"{safe_filename}.yaml"

            if dry_run:
                click.echo(f"  📁 Would create: {yaml_file}")
                if verbose:
                    preview = yaml.dump(yaml_content, default_flow_style=False)[:300]
                    click.echo(f"    {preview}...")
                created_files.append(yaml_file)
            else:
                mcp_dir.mkdir(parents=True, exist_ok=True)
                with open(yaml_file, "w", encoding="utf-8") as f:
                    yaml.dump(
                        yaml_content, f, default_flow_style=False, sort_keys=False
                    )
                click.echo(f"✅ Generated: {yaml_file}")
                created_files.append(yaml_file)

        return created_files

    def _generate_individual_prompt_files(
        self,
        commands: List[Any],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate individual markdown files for each slash command in .continue/prompts/."""
        prompts_dir = output_dir / ".continue" / "prompts"
        created_files = []

        for command in commands:
            # Apply variable substitution to prompt
            # Apply variable substitution to prompt
            command_prompt = command.prompt
            if variables:
                for var_name, var_value in variables.items():
                    placeholder = "{{{ " + var_name + " }}}"
                    command_prompt = command_prompt.replace(placeholder, var_value)

            # Build frontmatter
            frontmatter = {
                "name": command.name,
                "description": command.description,
                "invokable": True,
            }

            # Add workflow-specific fields
            if command.requires_approval:
                frontmatter["requiresApproval"] = True

            # Add workflow-specific fields
            # Infer multiStep from presence of steps or tool_calls (or explicit multi_step)
            if command.multi_step or command.steps or command.tool_calls:
                frontmatter["multiStep"] = True
            if command.tool_calls:
                frontmatter["toolCalls"] = command.tool_calls
            if command.steps:
                frontmatter["steps"] = [
                    {
                        "name": step.name,
                        "action": step.action,
                        **(
                            {"description": step.description}
                            if step.description
                            else {}
                        ),
                        **({"params": step.params} if step.params else {}),
                        **({"conditions": step.conditions} if step.conditions else {}),
                    }
                    for step in command.steps
                ]

            lines = ["---"]
            yaml_fm = yaml.safe_dump(
                frontmatter, default_flow_style=False, sort_keys=False
            ).strip()
            lines.append(yaml_fm)
            lines.append("---")
            lines.append("")
            lines.append(command_prompt)

            md_content = "\n".join(lines)

            # Write markdown file with sanitized filename
            safe_filename = self._sanitize_filename(command.name)
            md_file = prompts_dir / f"{safe_filename}.md"

            if dry_run:
                click.echo(f"  📁 Would create: {md_file}")
                if verbose:
                    preview = (
                        md_content[:300] + "..."
                        if len(md_content) > 300
                        else md_content
                    )
                    click.echo(f"    {preview}")
                created_files.append(md_file)
            else:
                prompts_dir.mkdir(parents=True, exist_ok=True)
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(md_content)
                click.echo(f"✅ Generated: {md_file}")
                created_files.append(md_file)

        return created_files

    def _generate_config_yaml(
        self,
        mcp_servers: Optional[List[Any]],
        commands: Optional[List[Any]],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Optional[Path]:
        """Generate .continue/config.yaml with metadata and prompt references."""
        config_path = output_dir / ".continue" / "config.yaml"

        # Build config structure
        config: Dict[str, Any] = {
            "name": "PrompTrek Generated Configuration",
            "version": "1.0.0",
            "schema": "v1",
        }

        # Add prompt references if commands present
        if commands:
            prompts_list = []
            for command in commands:
                safe_filename = self._sanitize_filename(command.name)
                prompts_list.append(
                    {"uses": f"file://.continue/prompts/{safe_filename}.md"}
                )
            config["prompts"] = prompts_list

        if dry_run:
            click.echo(f"  📁 Would create: {config_path}")
            if verbose:
                preview = yaml.dump(config, default_flow_style=False)[:300]
                click.echo(f"    {preview}...")
        else:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            click.echo(f"✅ Generated: {config_path}")

        return config_path

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

    def validate(
        self, prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]
    ) -> List[ValidationError]:
        """Validate prompt for Continue."""
        errors = []

        # V2/V3 validation: check content exists
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            if not prompt.content or not prompt.content.strip():
                errors.append(
                    ValidationError(
                        field="content",
                        message="Continue requires content",
                        severity="error",
                    )
                )
            return errors

        # V1 validation: Continue requires a system message
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

    def _build_continue_frontmatter(
        self,
        name: str,
        description: Optional[str] = None,
        globs: Optional[str] = None,
        always_apply: bool = False,
    ) -> Dict[str, Any]:
        """Build Continue frontmatter from metadata fields."""
        fm: Dict[str, Any] = {"name": name}
        if description:
            fm["description"] = description
        if globs:
            fm["globs"] = globs
        fm["alwaysApply"] = always_apply
        return fm

    def _build_md_file_with_frontmatter(
        self,
        frontmatter: Dict[str, Any],
        content: str,
        variables: Optional[Dict[str, Any]],
    ) -> str:
        """Build complete markdown file with YAML frontmatter and content."""
        lines = ["---"]
        # Use yaml.safe_dump to serialize frontmatter correctly
        yaml_frontmatter = yaml.safe_dump(
            frontmatter, default_flow_style=False, sort_keys=False
        ).strip()
        lines.append(yaml_frontmatter)
        lines.append("---")
        lines.append("")

        # Apply variable substitution to content
        if variables:
            for var_name, var_value in variables.items():
                placeholder = "{{{ " + var_name + " }}}"
                content = content.replace(placeholder, var_value)

        lines.append(content)
        return "\n".join(lines)

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

    def parse_files(
        self, source_dir: Path
    ) -> Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]:
        """
        Parse Continue files back into UniversalPromptV3.

        Uses v3.0 format with documents field for lossless multi-file sync and clean top-level plugin structure.

        Args:
            source_dir: Directory containing Continue configuration files

        Returns:
            UniversalPromptV3 object parsed from Continue files
        """
        # Parse markdown files from .continue/rules/
        rules_dir = source_dir / ".continue" / "rules"

        if not rules_dir.exists():
            # Fallback to v1 parsing if no rules directory
            return self._parse_files_v1(source_dir)

        # V3: Parse each markdown file as a document
        documents = []
        main_content = None

        for md_file in sorted(rules_dir.glob("*.md")):
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse frontmatter if present
                doc_name = md_file.stem  # Remove .md extension
                doc_description = None
                doc_always_apply = None
                doc_file_globs = None
                actual_content = content.strip()

                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        try:
                            frontmatter = yaml.safe_load(parts[1])
                            actual_content = parts[2].strip()

                            # Extract frontmatter fields
                            if frontmatter:
                                doc_name = frontmatter.get("name", doc_name)
                                doc_description = frontmatter.get("description")
                                doc_always_apply = frontmatter.get("alwaysApply")
                                # Continue uses 'applyToFiles' for file globs
                                doc_file_globs = frontmatter.get("applyToFiles")
                        except Exception:
                            # If frontmatter parsing fails, use full content
                            pass

                # Special handling: general.md becomes the main content field
                # This is the default file generated by PrompTrek and should not be renamed
                # All other .md files in .continue/rules/ become documents
                if md_file.stem == "general":
                    main_content = actual_content
                else:
                    # Otherwise, create a document for this file
                    documents.append(
                        DocumentConfig(
                            name=doc_name,
                            content=actual_content,
                            description=doc_description,
                            always_apply=doc_always_apply,
                            file_globs=doc_file_globs,
                        )
                    )

            except Exception as e:
                click.echo(f"Warning: Could not parse {md_file}: {e}")

        # Parse MCP servers from .continue/mcpServers/*.yaml
        mcp_servers = []
        mcp_dir = source_dir / ".continue" / "mcpServers"
        if mcp_dir.exists():
            for yaml_file in sorted(mcp_dir.glob("*.yaml")):
                try:
                    with open(yaml_file, "r", encoding="utf-8") as f:
                        yaml_content = yaml.safe_load(f)

                    # Parse Continue's MCP server format
                    if yaml_content and "mcpServers" in yaml_content:
                        for server_config in yaml_content["mcpServers"]:
                            from promptrek.core.models import MCPServer

                            mcp_servers.append(
                                MCPServer(
                                    name=server_config.get("name"),
                                    command=server_config.get("command"),
                                    args=server_config.get("args"),
                                    env=server_config.get("env"),
                                )
                            )
                except Exception as e:
                    click.echo(f"Warning: Could not parse {yaml_file}: {e}")

        # Parse slash commands from .continue/prompts/*.md
        commands = []
        prompts_dir = source_dir / ".continue" / "prompts"
        if prompts_dir.exists():
            for md_file in sorted(prompts_dir.glob("*.md")):
                try:
                    with open(md_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Parse frontmatter
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            frontmatter = yaml.safe_load(parts[1])
                            prompt_content = parts[2].strip()

                            from promptrek.core.models import Command

                            command = Command(
                                name=frontmatter.get("name", md_file.stem),
                                description=frontmatter.get("description", ""),
                                prompt=prompt_content,
                            )

                            # Skip spec commands (they are auto-injected during generate)
                            if not command.name.startswith("promptrek.spec."):
                                commands.append(command)
                except Exception as e:
                    click.echo(f"Warning: Could not parse {md_file}: {e}")

        # Parse metadata from .continue/config.yaml if it exists
        config_yaml = source_dir / ".continue" / "config.yaml"
        if config_yaml.exists():
            try:
                with open(config_yaml, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)

                # Use config metadata if available
                metadata = PromptMetadata(
                    title=config.get("name", "Continue AI Assistant"),
                    description="Configuration synced from Continue",
                    version=config.get("version", "1.0.0"),
                    author="PrompTrek Sync",
                    created=datetime.now().isoformat(),
                    updated=datetime.now().isoformat(),
                    tags=["continue", "synced"],
                )
            except Exception as e:
                click.echo(f"Warning: Could not parse config.yaml: {e}")
                metadata = PromptMetadata(
                    title="Continue AI Assistant",
                    description="Configuration synced from Continue rules",
                    version="1.0.0",
                    author="PrompTrek Sync",
                    created=datetime.now().isoformat(),
                    updated=datetime.now().isoformat(),
                    tags=["continue", "synced"],
                )
        else:
            # Create default metadata
            metadata = PromptMetadata(
                title="Continue AI Assistant",
                description="Configuration synced from Continue rules",
                version="1.0.0",
                author="PrompTrek Sync",
                created=datetime.now().isoformat(),
                updated=datetime.now().isoformat(),
                tags=["continue", "synced"],
            )

        # Use main content from general.md or provide default
        if not main_content:
            main_content = "# Continue AI Assistant\n\nNo rules found."

        return UniversalPromptV3(
            schema_version="3.0.0",
            metadata=metadata,
            content=main_content,
            documents=documents if documents else None,
            mcp_servers=mcp_servers if mcp_servers else None,
            commands=commands if commands else None,
            variables={},
        )

    def _parse_files_v1(self, source_dir: Path) -> UniversalPrompt:
        """
        Parse Continue files back into v1 UniversalPrompt (legacy).

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
