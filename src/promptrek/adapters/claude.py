"""
Claude Code adapter implementation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import click
import yaml

from ..core.exceptions import DeprecationWarnings, ValidationError
from ..core.models import UniversalPrompt, UniversalPromptV2, UniversalPromptV3
from .base import EditorAdapter
from .sync_mixin import SingleFileMarkdownSyncMixin


class ClaudeAdapter(SingleFileMarkdownSyncMixin, EditorAdapter):
    """Adapter for Claude Code."""

    _description = "Claude Code (context-based)"
    _file_patterns = [".claude/CLAUDE.md", ".claude-context.md"]

    def __init__(self) -> None:
        super().__init__(
            name="claude",
            description=self._description,
            file_patterns=self._file_patterns,
        )

    def generate(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> List[Path]:
        """Generate Claude Code context files."""

        # Determine output path
        claude_dir = output_dir / ".claude"
        output_file = claude_dir / "CLAUDE.md"

        # Check if this is v3/v2 (simplified) or v1 (complex)
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            # V2/V3: Direct markdown output (lossless!)
            content = prompt.content

            # Merge variables: prompt variables + CLI/local overrides
            merged_vars = {}
            if prompt.variables:
                merged_vars.update(prompt.variables)
            if variables:
                merged_vars.update(variables)

            # Apply variable substitution if variables provided
            if merged_vars:
                for var_name, var_value in merged_vars.items():
                    # Replace {{{ VAR_NAME }}} with value
                    placeholder = "{{{ " + var_name + " }}}"
                    content = content.replace(placeholder, var_value)
        else:
            # V1: Build content from structured fields
            processed_prompt = self.substitute_variables(prompt, variables)
            assert isinstance(
                processed_prompt, UniversalPrompt
            ), "V1 path should have UniversalPrompt"
            conditional_content = self.process_conditionals(processed_prompt, variables)
            content = self._build_content(processed_prompt, conditional_content)

        if dry_run:
            click.echo(f"  📁 Would create: {output_file}")
            if verbose:
                click.echo("  📄 Content preview:")
                preview = content[:200] + "..." if len(content) > 200 else content
                click.echo(f"    {preview}")
        else:
            # Create directory and file
            claude_dir.mkdir(exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"✅ Generated: {output_file}")

        generated_files = [output_file]

        # Generate plugin files for v2.1/v3.0
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            # Merge variables for plugins too
            merged_vars = {}
            if prompt.variables:
                merged_vars.update(prompt.variables)
            if variables:
                merged_vars.update(variables)

            # Check for v3 top-level fields first, then v2.1 nested structure
            plugin_files = self._generate_plugins(
                prompt,
                output_dir,
                dry_run,
                verbose,
                merged_vars if merged_vars else None,
            )
            generated_files.extend(plugin_files)

        return generated_files

    def generate_multiple(
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
        """Generate separate Claude context files for each prompt file."""

        claude_dir = output_dir / ".claude"
        generated_files = []

        for prompt, source_file in prompt_files:
            # Only support v1 prompts in generate_multiple (for now)
            # V2/V3 prompts should use the main generate() method
            if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
                click.echo(
                    f"⚠️  Skipping v2/v3 prompt from {source_file} (use generate() instead)"
                )
                continue

            # Apply variable substitution if supported
            processed_prompt = self.substitute_variables(prompt, variables)
            assert isinstance(
                processed_prompt, UniversalPrompt
            ), "V1 path should have UniversalPrompt"

            # Process conditionals if supported
            conditional_content = self.process_conditionals(processed_prompt, variables)

            # Create content
            content = self._build_content(processed_prompt, conditional_content)

            # Generate filename based on source file name
            # Remove .promptrek.yaml and add .md extension
            base_name = source_file.stem
            if base_name.endswith(".promptrek"):
                base_name = base_name.removesuffix(
                    ".promptrek"
                )  # Remove .promptrek suffix
            output_file = claude_dir / f"{base_name}.md"

            if dry_run:
                click.echo(f"  📁 Would create: {output_file}")
                if verbose:
                    click.echo("  📄 Content preview:")
                    preview = content[:200] + "..." if len(content) > 200 else content
                    click.echo(f"    {preview}")
            else:
                # Create directory and file
                claude_dir.mkdir(exist_ok=True)
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(content)
                click.echo(f"✅ Generated: {output_file}")

            generated_files.append(output_file)

        return generated_files

    def validate(
        self, prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]
    ) -> List[ValidationError]:
        """Validate prompt for Claude."""
        errors = []

        # V2/V3 validation: just check content exists
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            if not prompt.content or not prompt.content.strip():
                errors.append(
                    ValidationError(
                        field="content",
                        message="Content cannot be empty",
                        severity="error",
                    )
                )
            return errors

        # V1 validation: check context and examples
        if not prompt.context:
            errors.append(
                ValidationError(
                    field="context",
                    message=(
                        "Claude works best with detailed project context " "information"
                    ),
                    severity="warning",
                )
            )

        if not prompt.examples:
            errors.append(
                ValidationError(
                    field="examples",
                    message=(
                        "Claude benefits from code examples for better " "understanding"
                    ),
                    severity="warning",
                )
            )

        return errors

    def supports_variables(self) -> bool:
        """Claude supports variable substitution."""
        return True

    def supports_conditionals(self) -> bool:
        """Claude supports conditional instructions."""
        return True

    def parse_files(
        self, source_dir: Path
    ) -> Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]:
        """
        Parse Claude Code files back into a UniversalPrompt.

        Uses v2 format by default for lossless sync (can be upgraded to v3).
        """
        file_path = ".claude/CLAUDE.md"
        # Use v2 sync for lossless roundtrip
        # Note: Parser will auto-upgrade to v3 if schema_version is 3.x.x
        return self.parse_single_markdown_file_v2(
            source_dir=source_dir,
            file_path=file_path,
            editor_name="Claude Code",
        )

    def _generate_plugins(
        self,
        prompt: Union[UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """
        Generate plugin files for Claude Code (v2.1 and v3.0 compatible).

        Checks for v3 top-level fields first, then falls back to v2.1 nested structure.
        """
        created_files = []
        claude_dir = output_dir / ".claude"

        # Extract plugin data from v3 top-level or v2.1 nested structure
        mcp_servers = None
        commands = None
        agents = None
        hooks = None

        if isinstance(prompt, UniversalPromptV3):
            # V3: Check top-level fields first
            mcp_servers = prompt.mcp_servers
            commands = prompt.commands
            agents = prompt.agents
            hooks = prompt.hooks
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
            if prompt.plugins.agents:
                click.echo(DeprecationWarnings.v3_nested_plugin_field_warning("agents"))
                agents = prompt.plugins.agents
            if prompt.plugins.hooks:
                click.echo(DeprecationWarnings.v3_nested_plugin_field_warning("hooks"))
                hooks = prompt.plugins.hooks

        # Generate MCP server configurations
        if mcp_servers:
            mcp_file = output_dir / ".mcp.json"  # Project root, per Claude Code docs
            mcp_servers_config = {}
            for server in mcp_servers:
                server_config: Dict[str, Any] = {
                    "command": server.command,
                    "type": "stdio",  # Default to stdio type per Claude Code docs
                }
                if server.args:
                    server_config["args"] = server.args
                if server.env:
                    # Apply variable substitution to env vars
                    env_vars = {}
                    for key, value in server.env.items():
                        substituted_value = value
                        if variables:
                            for var_name, var_value in variables.items():
                                placeholder = "{{{ " + var_name + " }}}"
                                substituted_value = substituted_value.replace(
                                    placeholder, var_value
                                )
                        env_vars[key] = substituted_value
                    server_config["env"] = env_vars
                mcp_servers_config[server.name] = server_config

            mcp_config = {"mcpServers": mcp_servers_config}

            if dry_run:
                click.echo(f"  📁 Would create: {mcp_file}")
                if verbose:
                    click.echo(f"    {json.dumps(mcp_config, indent=2)[:200]}...")
            else:
                # MCP file goes in project root, no need to create claude_dir
                with open(mcp_file, "w", encoding="utf-8") as f:
                    json.dump(mcp_config, f, indent=2)
                click.echo(f"✅ Generated: {mcp_file}")
            created_files.append(mcp_file)

        # Generate slash commands
        if commands:
            commands_dir = claude_dir / "commands"
            for command in commands:
                # Apply variable substitution
                command_prompt = command.prompt
                if variables:
                    for var_name, var_value in variables.items():
                        placeholder = "{{{ " + var_name + " }}}"
                        command_prompt = command_prompt.replace(placeholder, var_value)

                command_file = commands_dir / f"{command.name}.md"
                content = self._build_command_content(command, command_prompt)

                if dry_run:
                    click.echo(f"  📁 Would create: {command_file}")
                    if verbose:
                        preview = (
                            content[:200] + "..." if len(content) > 200 else content
                        )
                        click.echo(f"    {preview}")
                else:
                    commands_dir.mkdir(parents=True, exist_ok=True)
                    with open(command_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    click.echo(f"✅ Generated: {command_file}")
                created_files.append(command_file)

        # Generate agents
        if agents:
            agents_dir = claude_dir / "agents"
            for agent in agents:
                # Apply variable substitution
                agent_prompt = agent.system_prompt
                if variables:
                    for var_name, var_value in variables.items():
                        placeholder = "{{{ " + var_name + " }}}"
                        agent_prompt = agent_prompt.replace(placeholder, var_value)

                agent_file = agents_dir / f"{agent.name}.md"
                content = self._build_agent_content(agent, agent_prompt)

                if dry_run:
                    click.echo(f"  📁 Would create: {agent_file}")
                    if verbose:
                        preview = (
                            content[:200] + "..." if len(content) > 200 else content
                        )
                        click.echo(f"    {preview}")
                else:
                    agents_dir.mkdir(parents=True, exist_ok=True)
                    with open(agent_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    click.echo(f"✅ Generated: {agent_file}")
                created_files.append(agent_file)

        # Generate hooks
        if hooks:
            hooks_file = claude_dir / "hooks.yaml"
            hooks_config = {
                "hooks": [
                    {
                        "name": hook.name,
                        "event": hook.event,
                        "command": hook.command,
                        **({"conditions": hook.conditions} if hook.conditions else {}),
                        "requires_reapproval": hook.requires_reapproval,
                    }
                    for hook in hooks
                ]
            }

            if dry_run:
                click.echo(f"  📁 Would create: {hooks_file}")
                if verbose:
                    click.echo(
                        f"    {yaml.dump(hooks_config, default_flow_style=False)[:200]}..."
                    )
            else:
                claude_dir.mkdir(parents=True, exist_ok=True)
                with open(hooks_file, "w", encoding="utf-8") as f:
                    yaml.dump(hooks_config, f, default_flow_style=False)
                click.echo(f"✅ Generated: {hooks_file}")
            created_files.append(hooks_file)

        return created_files

    def _build_command_content(self, command: Any, prompt: str) -> str:
        """Build markdown content for a slash command."""
        lines = []
        lines.append(f"# {command.name}")
        lines.append("")
        lines.append(f"**Description:** {command.description}")
        lines.append("")

        if command.system_message:
            lines.append("## System Message")
            lines.append(command.system_message)
            lines.append("")

        lines.append("## Prompt")
        lines.append(prompt)
        lines.append("")

        if command.examples:
            lines.append("## Examples")
            for example in command.examples:
                lines.append(f"- {example}")
            lines.append("")

        if command.trust_metadata:
            lines.append("## Trust Metadata")
            lines.append(f"- Trusted: {command.trust_metadata.trusted}")
            lines.append(
                f"- Requires Approval: {command.trust_metadata.requires_approval}"
            )
            lines.append("")

        return "\n".join(lines)

    def _build_agent_content(self, agent: Any, system_prompt: str) -> str:
        """Build markdown content for an agent."""
        lines = []
        lines.append(f"# {agent.name}")
        lines.append("")
        lines.append(f"**Description:** {agent.description}")
        lines.append("")

        lines.append("## System Prompt")
        lines.append(system_prompt)
        lines.append("")

        if agent.tools:
            lines.append("## Available Tools")
            for tool in agent.tools:
                lines.append(f"- {tool}")
            lines.append("")

        lines.append("## Configuration")
        lines.append(f"- Trust Level: {agent.trust_level}")
        lines.append(f"- Requires Approval: {agent.requires_approval}")
        lines.append("")

        if agent.context:
            lines.append("## Additional Context")
            for key, value in agent.context.items():
                lines.append(f"- **{key}**: {value}")
            lines.append("")

        return "\n".join(lines)

    def _build_content(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build Claude Code context content."""
        lines = []

        # Header with clear context
        lines.append(f"# {prompt.metadata.title}")
        lines.append("")
        lines.append("## Project Overview")
        lines.append(prompt.metadata.description)
        lines.append("")

        # Project context is crucial for Claude
        if prompt.context:
            lines.append("## Project Details")
            if prompt.context.project_type:
                lines.append(f"**Project Type:** {prompt.context.project_type}")
            if prompt.context.technologies:
                lines.append(
                    f"**Technologies:** {', '.join(prompt.context.technologies)}"
                )
            if prompt.context.description:
                lines.append("")
                lines.append("**Description:**")
                lines.append(prompt.context.description)
            lines.append("")

        # Instructions organized for Claude's understanding
        if prompt.instructions or (
            conditional_content and "instructions" in conditional_content
        ):
            lines.append("## Development Guidelines")

            # Combine original and conditional instructions
            all_instructions = prompt.instructions if prompt.instructions else None

            if all_instructions and all_instructions.general:
                lines.append("### General Principles")
                for instruction in all_instructions.general:
                    lines.append(f"- {instruction}")

                # Add conditional general instructions
                if (
                    conditional_content
                    and "instructions" in conditional_content
                    and "general" in conditional_content["instructions"]
                ):
                    for instruction in conditional_content["instructions"]["general"]:
                        lines.append(f"- {instruction}")
                lines.append("")
            elif (
                conditional_content
                and "instructions" in conditional_content
                and "general" in conditional_content["instructions"]
            ):
                lines.append("### General Principles")
                for instruction in conditional_content["instructions"]["general"]:
                    lines.append(f"- {instruction}")
                lines.append("")

            if all_instructions and all_instructions.code_style:
                lines.append("### Code Style Requirements")
                for guideline in all_instructions.code_style:
                    lines.append(f"- {guideline}")
                lines.append("")

            if all_instructions and all_instructions.testing:
                lines.append("### Testing Standards")
                for guideline in all_instructions.testing:
                    lines.append(f"- {guideline}")
                lines.append("")

            # Add architecture guidelines if present
            if (
                all_instructions
                and hasattr(all_instructions, "architecture")
                and all_instructions.architecture
            ):
                lines.append("### Architecture Guidelines")
                for guideline in all_instructions.architecture:
                    lines.append(f"- {guideline}")
                lines.append("")

        # Examples are very useful for Claude
        examples_to_show = {}
        if prompt.examples:
            examples_to_show.update(prompt.examples)

        # Add conditional examples
        if conditional_content and "examples" in conditional_content:
            examples_to_show.update(conditional_content["examples"])

        if examples_to_show:
            lines.append("## Code Examples")
            lines.append("")
            lines.append(
                "The following examples demonstrate the expected code patterns "
                "and style:"
            )
            lines.append("")

            for name, example in examples_to_show.items():
                lines.append(f"### {name.replace('_', ' ').title()}")
                lines.append(example)
                lines.append("")

        # Claude-specific instructions
        lines.append("## AI Assistant Instructions")
        lines.append("")
        lines.append("When working on this project:")
        lines.append("- Follow the established patterns and conventions shown above")
        lines.append("- Maintain consistency with the existing codebase")
        lines.append(
            "- Consider the project context and requirements in all " "suggestions"
        )
        lines.append("- Prioritize code quality, maintainability, and best practices")
        if prompt.context and prompt.context.technologies:
            tech_list = ", ".join(prompt.context.technologies)
            lines.append(f"- Leverage {tech_list} best practices and idioms")

        return "\n".join(lines)
