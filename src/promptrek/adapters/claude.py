"""
Claude Code adapter implementation.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import click
import yaml

from ..core.exceptions import DeprecationWarnings, ValidationError
from ..core.models import Agent, UniversalPrompt, UniversalPromptV2, UniversalPromptV3
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

        Uses v3.0 format for lossless sync with clean top-level plugin structure.
        Parses main CLAUDE.md plus any plugin files (agents, commands, hooks, MCP).
        """
        file_path = ".claude/CLAUDE.md"
        # Use v3 sync for lossless roundtrip with clean top-level plugins
        prompt = self.parse_single_markdown_file_v3(
            source_dir=source_dir,
            file_path=file_path,
            editor_name="Claude Code",
        )

        # Parse additional plugin files
        agents = self._parse_agent_files(source_dir)
        commands = self._parse_command_files(source_dir)
        hooks = self._parse_hooks_file(source_dir)
        mcp_servers = self._parse_mcp_file(source_dir)

        # Add plugins to prompt
        if agents:
            prompt.agents = agents
        if commands:
            prompt.commands = commands
        if hooks:
            prompt.hooks = hooks
        if mcp_servers:
            prompt.mcp_servers = mcp_servers

        return prompt

    def _parse_agent_files(self, source_dir: Path) -> Optional[List[Any]]:
        """Parse agent files from .claude/agents/ directory."""
        agents_dir = source_dir / ".claude" / "agents"
        if not agents_dir.exists():
            return None

        agents = []
        for agent_file in agents_dir.glob("*.md"):
            try:
                with open(agent_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Try frontmatter format first
                frontmatter, remaining = self._extract_frontmatter_from_content(content)

                if frontmatter:
                    # Parse frontmatter format
                    # Content after frontmatter is the prompt
                    prompt_content = remaining.strip() if remaining else ""

                    # Description is optional from frontmatter
                    description_raw = frontmatter.get("description")
                    description: Optional[str] = None
                    if description_raw and isinstance(description_raw, str):
                        description = description_raw.replace("\\n", "\n")

                    # Parse tools - handle both list and comma-separated string
                    tools_raw = frontmatter.get("tools")
                    tools: Optional[List[str]] = None
                    if tools_raw:
                        if isinstance(tools_raw, str):
                            # Split comma-separated string into list
                            tools = [t.strip() for t in tools_raw.split(",")]
                        elif isinstance(tools_raw, list):
                            tools = tools_raw

                    agent = Agent(
                        name=frontmatter.get("name", agent_file.stem),
                        prompt=prompt_content,  # type: ignore[call-arg]  # Pydantic alias: prompt/system_prompt
                        description=description,
                        tools=tools,
                        trust_level=frontmatter.get("trust_level", "untrusted"),
                        requires_approval=frontmatter.get("requires_approval", True),
                        context=frontmatter.get("context"),
                    )
                else:
                    # Parse markdown format (no frontmatter - just pure markdown)
                    # Extract name from # heading
                    name_match = re.match(r"^#\s+(.+?)$", content, re.MULTILINE)
                    name = (
                        name_match.group(1).strip() if name_match else agent_file.stem
                    )

                    # Extract description (between **Description:** and next content)
                    # This is optional metadata that we add during generation
                    desc_match = re.search(
                        r"\*\*Description:\*\*\s+(.*?)(?=\n\n|\Z)", content, re.DOTALL
                    )
                    description = desc_match.group(1).strip() if desc_match else None

                    # Extract the actual prompt content (everything after heading and description)
                    # Remove the heading line
                    prompt_content = content
                    if name_match:
                        # Remove heading and everything up to first blank line after it
                        prompt_content = re.sub(
                            r"^#\s+.+?\n+", "", prompt_content, count=1
                        )

                    # Remove description if present
                    if desc_match:
                        prompt_content = re.sub(
                            r"\*\*Description:\*\*\s+.*?\n+",
                            "",
                            prompt_content,
                            count=1,
                        )

                    prompt_content = prompt_content.strip()

                    # Extract tools (after ## Available Tools)
                    tools = None
                    tools_match = re.search(
                        r"##\s+Available Tools\s+(.*?)(?=##|\Z)", content, re.DOTALL
                    )
                    if tools_match:
                        tools_text = tools_match.group(1).strip()
                        # Parse list items
                        tools = [
                            line.strip("- ").strip()
                            for line in tools_text.split("\n")
                            if line.strip().startswith("-")
                        ]

                    # Extract configuration (trust level and requires approval)
                    trust_level = "untrusted"
                    requires_approval = True
                    config_match = re.search(
                        r"##\s+Configuration\s+(.*?)(?=##|\Z)", content, re.DOTALL
                    )
                    if config_match:
                        config_text = config_match.group(1)
                        trust_match = re.search(r"Trust Level:\s*(\w+)", config_text)
                        if trust_match:
                            trust_level = trust_match.group(1).lower()
                        approval_match = re.search(
                            r"Requires Approval:\s*(True|False)", config_text
                        )
                        if approval_match:
                            requires_approval = approval_match.group(1) == "True"

                    # Extract context (after ## Additional Context)
                    context = None
                    context_match = re.search(
                        r"##\s+Additional Context\s+(.*?)(?=##|\Z)", content, re.DOTALL
                    )
                    if context_match:
                        context_text = context_match.group(1).strip()
                        context = {}
                        for line in context_text.split("\n"):
                            kv_match = re.match(
                                r"-\s+\*\*(.+?)\*\*:\s*(.+)", line.strip()
                            )
                            if kv_match:
                                context[kv_match.group(1)] = kv_match.group(2)

                    agent = Agent(
                        name=name,
                        prompt=prompt_content,  # type: ignore[call-arg]  # Pydantic alias: prompt/system_prompt
                        description=description,
                        tools=tools if tools else None,
                        trust_level=trust_level,
                        requires_approval=requires_approval,
                        context=context,
                    )

                agents.append(agent)

            except Exception as e:
                click.echo(f"⚠️  Error parsing agent file {agent_file}: {e}")

        return agents if agents else None

    def _parse_command_files(self, source_dir: Path) -> Optional[List[Any]]:
        """Parse command files from .claude/commands/ directory."""
        from ..core.models import Command

        commands_dir = source_dir / ".claude" / "commands"
        if not commands_dir.exists():
            return None

        commands = []
        for command_file in commands_dir.glob("*.md"):
            try:
                with open(command_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Try frontmatter format first
                frontmatter, remaining = self._extract_frontmatter_from_content(content)

                if frontmatter:
                    # Parse frontmatter format
                    description = frontmatter.get("description", "")
                    if description and isinstance(description, str):
                        description = description.replace("\\n", "\n")

                    command = Command(
                        name=frontmatter.get("name", command_file.stem),
                        description=description,
                        prompt=remaining.strip(),
                        output_format=frontmatter.get("output_format"),
                        requires_approval=frontmatter.get("requires_approval", False),
                        examples=frontmatter.get("examples"),
                        trust_metadata=frontmatter.get("trust_metadata"),
                    )
                else:
                    # Parse markdown format (generated by _build_command_content)
                    # Extract name from # heading
                    name_match = re.match(r"^#\s+(.+?)$", content, re.MULTILINE)
                    name = (
                        name_match.group(1).strip() if name_match else command_file.stem
                    )

                    # Extract description (between **Description:** and next ## heading)
                    desc_match = re.search(
                        r"\*\*Description:\*\*\s+(.*?)(?=##|\Z)", content, re.DOTALL
                    )
                    description = desc_match.group(1).strip() if desc_match else ""

                    # Extract required tools for workflows
                    tool_calls = None
                    tools_match = re.search(
                        r"##\s+Required Tools\s*\n\n((?:- `[^`]+`\n?)+)",
                        content,
                        re.MULTILINE,
                    )
                    if tools_match:
                        tool_lines = tools_match.group(1).strip().split("\n")
                        tool_calls = []
                        for line in tool_lines:
                            tool_match = re.search(r"`([^`]+)`", line)
                            if tool_match:
                                tool_calls.append(tool_match.group(1))

                    # Infer multi_step from presence of tool_calls or workflow sections
                    # (no need to parse the text "Type: Multi-step Workflow")
                    multi_step = bool(tool_calls)

                    # Extract prompt (after ## Prompt)
                    prompt_match = re.search(
                        r"##\s+Prompt\s+(.*?)(?=##|\Z)", content, re.DOTALL
                    )
                    prompt = prompt_match.group(1).strip() if prompt_match else ""

                    # Extract examples (after ## Examples)
                    examples = None
                    examples_match = re.search(
                        r"##\s+Examples\s+(.*?)(?=##|\Z)", content, re.DOTALL
                    )
                    if examples_match:
                        examples_text = examples_match.group(1).strip()
                        # Parse list items
                        examples = [
                            line.strip("- ").strip()
                            for line in examples_text.split("\n")
                            if line.strip().startswith("-")
                        ]

                    command = Command(
                        name=name,
                        description=description,
                        prompt=prompt,
                        output_format=None,
                        requires_approval=False,
                        examples=examples if examples else None,
                        trust_metadata=None,
                        multi_step=multi_step,
                        tool_calls=tool_calls,
                    )

                commands.append(command)

            except Exception as e:
                click.echo(f"⚠️  Error parsing command file {command_file}: {e}")

        return commands if commands else None

    def _parse_hooks_file(self, source_dir: Path) -> Optional[List[Any]]:
        """Parse hooks from .claude/hooks.yaml or .claude/settings.local.json file."""
        from ..core.models import Hook

        # Try hooks.yaml first (PrompTrek format)
        hooks_yaml = source_dir / ".claude" / "hooks.yaml"
        if hooks_yaml.exists():
            try:
                with open(hooks_yaml, "r", encoding="utf-8") as f:
                    hooks_config = yaml.safe_load(f)

                if hooks_config and "hooks" in hooks_config:
                    hooks = []
                    for hook_data in hooks_config["hooks"]:
                        hook = Hook(
                            name=hook_data.get("name"),
                            event=hook_data.get("event"),
                            command=hook_data.get("command"),
                            conditions=hook_data.get("conditions"),
                            requires_reapproval=hook_data.get(
                                "requires_reapproval", True
                            ),
                            description=hook_data.get("description"),
                        )
                        hooks.append(hook)
                    return hooks if hooks else None

            except Exception as e:
                click.echo(f"⚠️  Error parsing hooks.yaml file: {e}")

        # Try settings.local.json (Claude Code native format)
        settings_file = source_dir / ".claude" / "settings.local.json"
        if settings_file.exists():
            try:
                with open(settings_file, "r", encoding="utf-8") as f:
                    settings_config = json.load(f)

                if not settings_config or "hooks" not in settings_config:
                    return None

                hooks = []
                hook_counter = 0
                # Parse Claude Code hooks format: {"PreToolUse": [{...}]}
                for event_type, event_configs in settings_config["hooks"].items():
                    for event_config in event_configs:
                        matcher = event_config.get("matcher")
                        # Each event_config has a "hooks" array with actual hook definitions
                        for hook_def in event_config.get("hooks", []):
                            hook_counter += 1
                            # Generate a name from event type and matcher
                            name_parts = [event_type.lower()]
                            if matcher:
                                name_parts.append(matcher.lower())
                            name = f"{'-'.join(name_parts)}-{hook_counter}"

                            conditions = {}
                            if matcher:
                                conditions["matcher"] = matcher

                            hook = Hook(
                                name=name,
                                event=event_type,
                                command=hook_def.get("command"),
                                conditions=conditions if conditions else None,
                                requires_reapproval=event_config.get(
                                    "requires_reapproval", True
                                ),
                                description=hook_def.get("description"),
                            )
                            hooks.append(hook)

                return hooks if hooks else None

            except Exception as e:
                click.echo(f"⚠️  Error parsing settings.local.json hooks: {e}")
                return None

        return None

    def _parse_mcp_file(self, source_dir: Path) -> Optional[List[Any]]:
        """Parse MCP servers from .mcp.json file."""
        from ..core.models import MCPServer

        mcp_file = source_dir / ".mcp.json"
        if not mcp_file.exists():
            return None

        try:
            with open(mcp_file, "r", encoding="utf-8") as f:
                mcp_config = json.load(f)

            if not mcp_config or "mcpServers" not in mcp_config:
                return None

            servers = []
            for server_name, server_config in mcp_config["mcpServers"].items():
                server = MCPServer(
                    name=server_name,
                    command=server_config.get("command"),
                    args=server_config.get("args"),
                    env=server_config.get("env"),
                    description=server_config.get("description"),
                    trust_metadata=server_config.get("trust_metadata"),
                )
                servers.append(server)

            return servers if servers else None

        except Exception as e:
            click.echo(f"⚠️  Error parsing MCP config file: {e}")
            return None

    def _extract_frontmatter_from_content(
        self, content: str
    ) -> tuple[Optional[Dict], str]:
        """
        Extract YAML frontmatter from markdown content.

        Handles both standard YAML and Claude Code native format with special chars.

        Returns:
            Tuple of (frontmatter_dict, remaining_content)
        """
        if not content.startswith("---"):
            return None, content

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None, content

        frontmatter_text = parts[1]
        remaining = parts[2].strip()

        # Try standard YAML parsing first
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            return frontmatter, remaining
        except yaml.YAMLError:
            # Fallback: manual parsing for Claude Code native format
            try:
                frontmatter = self._parse_frontmatter_manually(frontmatter_text)
                return frontmatter, remaining
            except Exception as e:
                click.echo(f"⚠️  Error parsing frontmatter: {e}")
                return None, content

    def _parse_frontmatter_manually(self, frontmatter_text: str) -> Dict[str, Any]:
        """
        Manually parse frontmatter that may contain YAML-incompatible content.

        This handles Claude Code native format where fields like 'description'
        may contain unquoted strings with colons and special characters.
        """
        frontmatter: Dict[str, Any] = {}
        current_key: Optional[str] = None
        current_value_lines: List[str] = []

        for line in frontmatter_text.split("\n"):
            # Check if this line starts a new key-value pair (no leading whitespace)
            if ": " in line and line.lstrip() == line:
                # Save previous key-value if exists
                if current_key:
                    value = "\n".join(current_value_lines).strip()
                    # Try to parse as YAML for structured values (lists, dicts)
                    try:
                        frontmatter[current_key] = yaml.safe_load(value)
                    except (yaml.YAMLError, ValueError, TypeError):
                        # If YAML parsing fails, keep as string
                        frontmatter[current_key] = value

                # Start new key-value pair
                key, value = line.split(": ", 1)
                current_key = key.strip()
                current_value_lines = [value]
            elif current_key:
                # Continuation of current value
                current_value_lines.append(line)

        # Save the last key-value pair
        if current_key:
            value = "\n".join(current_value_lines).strip()
            try:
                frontmatter[current_key] = yaml.safe_load(value)
            except (yaml.YAMLError, ValueError, TypeError):
                frontmatter[current_key] = value

        return frontmatter

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
                agent_prompt = agent.prompt
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
            # Separate hooks by type: those with matchers go to settings.local.json,
            # others go to hooks.yaml
            hooks_with_matchers = []
            hooks_without_matchers = []

            for hook in hooks:
                if hook.conditions and "matcher" in hook.conditions:
                    hooks_with_matchers.append(hook)
                else:
                    hooks_without_matchers.append(hook)

            # Generate settings.local.json for hooks with matchers (Claude Code native format)
            if hooks_with_matchers:
                settings_file = claude_dir / "settings.local.json"

                # Group hooks by event type
                hooks_by_event: Dict[str, List[Any]] = {}
                for hook in hooks_with_matchers:
                    event = hook.event
                    if event not in hooks_by_event:
                        hooks_by_event[event] = []

                    # Build Claude Code format (conditions already validated above)
                    if not hook.conditions or "matcher" not in hook.conditions:
                        continue  # Skip if conditions invalid

                    hook_config = {
                        "matcher": hook.conditions["matcher"],
                        "hooks": [
                            {
                                "type": "command",
                                "command": hook.command,
                            }
                        ],
                    }
                    hooks_by_event[event].append(hook_config)

                settings_config = {"hooks": hooks_by_event}

                if dry_run:
                    click.echo(f"  📁 Would create: {settings_file}")
                    if verbose:
                        click.echo(
                            f"    {json.dumps(settings_config, indent=2)[:200]}..."
                        )
                else:
                    claude_dir.mkdir(parents=True, exist_ok=True)

                    # Merge with existing settings.local.json if it exists
                    if settings_file.exists():
                        try:
                            with open(settings_file, "r", encoding="utf-8") as f:
                                existing_config = json.load(f)
                            # Merge hooks section
                            if "hooks" in existing_config:
                                for event, event_hooks in hooks_by_event.items():
                                    if event in existing_config["hooks"]:
                                        existing_config["hooks"][event].extend(
                                            event_hooks
                                        )
                                    else:
                                        existing_config["hooks"][event] = event_hooks
                                settings_config = existing_config
                            else:
                                settings_config.update(existing_config)
                        except Exception as e:
                            click.echo(
                                f"⚠️  Error reading existing settings.local.json: {e}"
                            )

                    with open(settings_file, "w", encoding="utf-8") as f:
                        json.dump(settings_config, f, indent=2)
                    click.echo(f"✅ Generated: {settings_file}")
                created_files.append(settings_file)

            # Generate hooks.yaml for hooks without matchers (PrompTrek format)
            if hooks_without_matchers:
                hooks_file = claude_dir / "hooks.yaml"
                hooks_config = {
                    "hooks": [
                        {
                            "name": hook.name,
                            "event": hook.event,
                            "command": hook.command,
                            **(
                                {"conditions": hook.conditions}
                                if hook.conditions
                                else {}
                            ),
                            "requires_reapproval": hook.requires_reapproval,
                        }
                        for hook in hooks_without_matchers
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
        """Build markdown content for a slash command or workflow."""
        lines = []
        lines.append(f"# {command.name}")
        lines.append("")
        lines.append(f"**Description:** {command.description}")
        lines.append("")

        # Check if this is a workflow (has steps or tool_calls)
        is_workflow = bool(command.steps or command.tool_calls)

        # Add workflow indicator if this is a workflow
        if is_workflow:
            lines.append("**Type:** Multi-step Workflow")
            lines.append("")

        # Add required tools for workflows
        if command.tool_calls:
            lines.append("## Required Tools")
            lines.append("")
            for tool in command.tool_calls:
                lines.append(f"- `{tool}`")
            lines.append("")

        lines.append("## Prompt")
        lines.append(prompt)
        lines.append("")

        # Add structured steps for workflows
        if command.steps:
            lines.append("## Workflow Steps")
            lines.append("")
            for i, step in enumerate(command.steps, 1):
                lines.append(f"### {i}. {step.name}")
                if step.description:
                    lines.append(f"   {step.description}")
                lines.append(f"   - Action: `{step.action}`")
                if step.params:
                    lines.append(f"   - Parameters: {step.params}")
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

    def _build_agent_content(self, agent: Any, agent_prompt: str) -> str:
        """Build markdown content for an agent.

        Creates Claude Code native YAML frontmatter format with agent metadata
        and the full prompt content after the frontmatter.

        Uses proper YAML serialization to handle complex values like multiline strings.
        """
        # Build frontmatter as a dictionary
        frontmatter_dict: Dict[str, Any] = {
            "name": agent.name,
        }

        # Add description if available
        if agent.description:
            frontmatter_dict["description"] = agent.description

        # Add model (default to sonnet if not specified)
        model = getattr(agent, "model", "sonnet")
        frontmatter_dict["model"] = model

        # Add tools if specified
        if agent.tools:
            frontmatter_dict["tools"] = agent.tools

        # Add trust level if specified
        if hasattr(agent, "trust_level") and agent.trust_level:
            frontmatter_dict["trust_level"] = agent.trust_level

        # Add requires_approval if specified
        if hasattr(agent, "requires_approval") and agent.requires_approval is not None:
            frontmatter_dict["requires_approval"] = agent.requires_approval

        # Add context if specified
        if hasattr(agent, "context") and agent.context:
            frontmatter_dict["context"] = agent.context

        # Serialize frontmatter as YAML
        frontmatter_yaml = yaml.dump(
            frontmatter_dict,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

        # Build final content
        lines = []
        lines.append("---")
        lines.append(
            frontmatter_yaml.rstrip()
        )  # Remove trailing newline from yaml.dump
        lines.append("---")
        lines.append("")
        lines.append(agent_prompt)

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
