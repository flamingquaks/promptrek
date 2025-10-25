"""
Amazon Q adapter implementation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import click

from ..core.exceptions import DeprecationWarnings, ValidationError
from ..core.models import UniversalPrompt, UniversalPromptV2, UniversalPromptV3
from .base import EditorAdapter
from .mcp_mixin import MCPGenerationMixin
from .sync_mixin import MarkdownSyncMixin

# Maximum number of instructions to include in agent configuration
MAX_AGENT_INSTRUCTIONS = 3


class AmazonQAdapter(MCPGenerationMixin, MarkdownSyncMixin, EditorAdapter):
    """Adapter for Amazon Q AI assistant."""

    _description = "Amazon Q (.amazonq/rules/, .amazonq/prompts/, .amazonq/cli-agents/)"
    _file_patterns = [
        ".amazonq/rules/*.md",
        ".amazonq/prompts/*.md",
        ".amazonq/cli-agents/*.json",
    ]

    def __init__(self) -> None:
        super().__init__(
            name="amazon-q",
            description=self._description,
            file_patterns=self._file_patterns,
        )

    def get_mcp_config_strategy(self) -> Dict[str, Any]:
        """Get MCP configuration strategy for Amazon Q adapter."""
        return {
            "supports_project": True,
            "project_path": ".amazonq/mcp.json",
            "system_path": str(Path.home() / ".aws" / "amazonq" / "mcp.json"),
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
        """Generate Amazon Q configuration files."""

        # V3: Always use plugin generation (handles rules + plugins)
        if isinstance(prompt, UniversalPromptV3):
            return self._generate_plugins(
                prompt, output_dir, dry_run, verbose, variables
            )

        # V2.1: Handle plugins if present
        if isinstance(prompt, UniversalPromptV2) and prompt.plugins:
            return self._generate_plugins(
                prompt, output_dir, dry_run, verbose, variables
            )

        # V2: Use documents field for multi-file rules or main content for single file (no plugins)
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

        # Note: V1 schema does not support agents/hooks via plugin fields
        # For v3 schema, use agents and hooks fields instead

        return created_files

    def _generate_v2(
        self,
        prompt: Union[UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate Amazon Q files from v2/v3 schema (using documents for rules or content for single file)."""
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

    def _generate_plugins(
        self,
        prompt: Union[UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate Amazon Q files from v2.1/v3.0 schema with plugin support."""
        created_files = []

        # First, generate the regular v2/v3 markdown files (rules)
        markdown_files = self._generate_v2(
            prompt, output_dir, dry_run, verbose, variables
        )
        created_files.extend(markdown_files)

        # Extract plugin fields (v3 only - we're focusing on v3.x)
        mcp_servers = None
        commands = None
        agents = None
        hooks = None

        if isinstance(prompt, UniversalPromptV3):
            # V3: Extract top-level plugin fields
            mcp_servers = prompt.mcp_servers
            commands = prompt.commands
            agents = prompt.agents
            hooks = prompt.hooks

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

        # Generate prompts from non-workflow commands
        if commands:
            prompts_files = self._generate_prompts(
                commands,
                output_dir,
                dry_run,
                verbose,
                variables,
            )
            created_files.extend(prompts_files)

        # Generate agents (agents will include hooks via injection)
        if agents:
            agent_files = self._generate_agents_v3(
                agents,
                hooks,
                output_dir,
                dry_run,
                verbose,
                variables,
            )
            created_files.extend(agent_files)
        elif hooks:
            # No agents but hooks exist - create default agent with hooks
            default_agent_files = self._generate_default_agent_with_hooks(
                hooks,
                output_dir,
                dry_run,
                verbose,
            )
            created_files.extend(default_agent_files)

        return created_files

    def _generate_mcp_config(
        self,
        mcp_servers: list,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate MCP configuration for Amazon Q."""
        strategy = self.get_mcp_config_strategy()
        created_files = []

        # Try project-level first (preferred)
        if strategy["supports_project"] and strategy["project_path"]:
            project_config_path = output_dir / strategy["project_path"]

            # Build MCP servers config (Amazon Q uses standard MCP format)
            mcp_config = self.build_mcp_servers_config(
                mcp_servers, variables, format_style="standard"
            )

            # Check if config already exists
            existing_config = self.read_existing_mcp_config(project_config_path)

            if existing_config:
                # Merge with existing config
                if verbose:
                    click.echo("  ℹ️  Merging MCP servers with existing Amazon Q config")
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

        # Fallback to system-wide if project-level failed
        elif strategy["system_path"]:
            system_path = Path(strategy["system_path"]).expanduser()

            # Build and write system-wide config
            mcp_config = self.build_mcp_servers_config(
                mcp_servers, variables, format_style="standard"
            )

            existing_config = self.read_existing_mcp_config(system_path)
            if existing_config:
                merged_config = self.merge_mcp_config(
                    existing_config, mcp_config, format_style="standard"
                )
            else:
                merged_config = mcp_config

            if self.write_mcp_config_file(merged_config, system_path, dry_run, verbose):
                created_files.append(system_path)

        return created_files

    def _generate_prompts(
        self,
        commands: list,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate .amazonq/prompts/*.md from non-workflow commands."""
        prompts_dir = output_dir / ".amazonq" / "prompts"
        created_files = []

        # Filter: only commands without steps/tool_calls (non-workflows)
        prompt_commands = [cmd for cmd in commands if not (cmd.steps or cmd.tool_calls)]

        for cmd in prompt_commands:
            # Build markdown content
            content_lines = [f"# {cmd.description}", ""]
            content_lines.append(cmd.prompt)

            content = "\n".join(content_lines)

            # Apply variable substitution
            if variables:
                for var_name, var_value in variables.items():
                    placeholder = "{{{ " + var_name + " }}}"
                    content = content.replace(placeholder, var_value)

            # Write file
            output_file = prompts_dir / f"{cmd.name}.md"

            if dry_run:
                click.echo(f"  📁 Would create: {output_file}")
                if verbose:
                    preview = content[:200] + "..." if len(content) > 200 else content
                    click.echo(f"    {preview}")
                created_files.append(output_file)
            else:
                prompts_dir.mkdir(parents=True, exist_ok=True)
                output_file.write_text(content, encoding="utf-8")
                click.echo(f"✅ Generated: {output_file}")
                created_files.append(output_file)

        return created_files

    def _map_hook_event(self, event: str) -> Optional[str]:
        """Map PrompTrek hook event to Amazon Q event."""
        event_map = {
            "prompt-submit": "userPromptSubmit",
            "agent-spawn": "agentSpawn",
        }
        return event_map.get(event)

    def _build_agent_hooks(
        self,
        agent_name: str,
        hooks: list,
    ) -> Optional[Dict[str, list]]:
        """
        Build Amazon Q hooks configuration for a specific agent.

        Includes:
        - Hooks with matching agent field
        - Hooks with no agent field (global hooks)

        Returns None if no applicable hooks.
        """
        agent_hooks_config = {}

        for hook in hooks:
            # Skip if hook is scoped to a different agent
            if hook.agent and hook.agent != agent_name:
                continue

            # Map event name to Amazon Q format
            amazon_q_event = self._map_hook_event(hook.event)
            if not amazon_q_event:
                # Unsupported event, skip
                continue

            # Build hook config
            hook_config = {"command": hook.command}

            # Add to event group
            if amazon_q_event not in agent_hooks_config:
                agent_hooks_config[amazon_q_event] = []
            agent_hooks_config[amazon_q_event].append(hook_config)

        return agent_hooks_config if agent_hooks_config else None

    def _generate_agents_v3(
        self,
        agents: list,
        hooks: Optional[list],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate .amazonq/cli-agents/*.json from v3 agents field."""
        agents_dir = output_dir / ".amazonq" / "cli-agents"
        created_files = []

        for agent in agents:
            # Build Amazon Q agent v1 schema
            agent_config = {
                "name": agent.name,
                "description": agent.description if agent.description else agent.name,
                "prompt": agent.prompt,
            }

            # Add tools if present
            if agent.tools:
                agent_config["tools"] = agent.tools

            # Always add resources pointing to rules
            agent_config["resources"] = ["file://.amazonq/rules/**/*.md"]

            # Inject hooks scoped to this agent
            if hooks:
                agent_hooks = self._build_agent_hooks(agent.name, hooks)
                if agent_hooks:
                    agent_config["hooks"] = agent_hooks

            # Apply variable substitution to prompt
            if variables:
                for var_name, var_value in variables.items():
                    placeholder = "{{{ " + var_name + " }}}"
                    agent_config["prompt"] = agent_config["prompt"].replace(
                        placeholder, var_value
                    )

            # Write file
            output_file = agents_dir / f"{agent.name}.json"

            if dry_run:
                click.echo(f"  📁 Would create: {output_file}")
                if verbose:
                    preview = json.dumps(agent_config, indent=2)[:200]
                    click.echo(f"    {preview}...")
                created_files.append(output_file)
            else:
                agents_dir.mkdir(parents=True, exist_ok=True)
                output_file.write_text(
                    json.dumps(agent_config, indent=2), encoding="utf-8"
                )
                click.echo(f"✅ Generated: {output_file}")
                created_files.append(output_file)

        return created_files

    def _generate_default_agent_with_hooks(
        self,
        hooks: list,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """
        Generate a default agent with global hooks when no agents are defined.
        Only creates agent if there are applicable hooks.
        """
        # Check if any hooks are supported by Amazon Q
        applicable_hooks = [
            hook for hook in hooks if self._map_hook_event(hook.event) is not None
        ]

        if not applicable_hooks:
            return []

        agents_dir = output_dir / ".amazonq" / "cli-agents"

        # Create minimal default agent
        default_agent = {
            "name": "default",
            "description": "Default assistant with project hooks",
            "prompt": "You are a helpful AI assistant.",
            "resources": ["file://.amazonq/rules/**/*.md"],
        }

        # Add hooks (all hooks since there's no agent filtering)
        hooks_config: Dict[str, list] = {}
        for hook in applicable_hooks:
            amazon_q_event = self._map_hook_event(hook.event)
            if amazon_q_event:
                if amazon_q_event not in hooks_config:
                    hooks_config[amazon_q_event] = []
                hooks_config[amazon_q_event].append({"command": hook.command})

        default_agent["hooks"] = hooks_config

        # Write file
        output_file = agents_dir / "default.json"

        if dry_run:
            click.echo(f"  📁 Would create: {output_file}")
            if verbose:
                preview = json.dumps(default_agent, indent=2)[:200]
                click.echo(f"    {preview}...")
            return [output_file]
        else:
            agents_dir.mkdir(parents=True, exist_ok=True)
            output_file.write_text(
                json.dumps(default_agent, indent=2), encoding="utf-8"
            )
            click.echo(f"✅ Generated: {output_file}")
            return [output_file]

    def _generate_rules_system(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        conditional_content: Optional[Dict[str, Any]],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate .amazonq/rules/ directory with markdown files."""
        rules_dir = output_dir / ".amazonq" / "rules"
        created_files = []

        # Generate general coding rules
        all_instructions: list[str] = []
        if (
            isinstance(prompt, UniversalPrompt)
            and prompt.instructions
            and prompt.instructions.general
        ):
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
                "General Rules", all_instructions
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
        if (
            isinstance(prompt, UniversalPrompt)
            and prompt.instructions
            and prompt.instructions.code_style
        ):
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
        if (
            isinstance(prompt, UniversalPrompt)
            and prompt.instructions
            and prompt.instructions.testing
        ):
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
        if (
            isinstance(prompt, UniversalPrompt)
            and prompt.instructions
            and prompt.instructions.security
        ):
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
        if (
            isinstance(prompt, UniversalPrompt)
            and prompt.context
            and prompt.context.technologies
        ):
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

    def _build_tech_rules_content(
        self,
        tech: str,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
    ) -> str:
        """Build technology-specific rules content."""
        lines = []

        lines.append(f"# {tech.title()} Rules")
        lines.append("")

        # Add general instructions that apply to this tech (V1 only)
        if (
            isinstance(prompt, UniversalPrompt)
            and prompt.instructions
            and prompt.instructions.general
        ):
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
        self, prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]
    ) -> List[ValidationError]:
        """Validate prompt for Amazon Q."""
        errors = []

        # V2/V3 validation: check content exists
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
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
    ) -> Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]:
        """Parse Amazon Q files back into a UniversalPrompt, UniversalPromptV2, or UniversalPromptV3."""
        return self.parse_markdown_rules_files(
            source_dir=source_dir,
            rules_subdir=".amazonq/rules",
            file_extension="md",
            editor_name="Amazon Q",
        )
