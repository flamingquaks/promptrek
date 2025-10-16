"""
Cursor editor adapter implementation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import click

from ..core.exceptions import DeprecationWarnings, ValidationError
from ..core.models import UniversalPrompt, UniversalPromptV2, UniversalPromptV3
from .base import EditorAdapter
from .sync_mixin import MarkdownSyncMixin


class CursorAdapter(MarkdownSyncMixin, EditorAdapter):
    """Adapter for Cursor editor."""

    _description = "Cursor (.cursor/rules/index.mdc, .cursor/rules/*.mdc, AGENTS.md)"
    _file_patterns = [".cursor/rules/index.mdc", ".cursor/rules/*.mdc", "AGENTS.md"]

    def __init__(self) -> None:
        super().__init__(
            name="cursor",
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
        """Generate Cursor configuration files."""

        # V2/V3: Use documents field for multi-file rules or main content for single file
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            return self._generate_v2(prompt, output_dir, dry_run, verbose, variables)

        # V1: Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)

        created_files = []

        # Generate main index.mdc for project overview
        index_file = self._generate_index_file(
            processed_prompt, output_dir, dry_run, verbose
        )
        created_files.extend(index_file)

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

    def _generate_v2(
        self,
        prompt: Union[UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate Cursor files from v2/v3 schema (using documents for rules or content for single file)."""
        rules_dir = output_dir / ".cursor" / "rules"
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
                    f"{doc.name}.mdc" if not doc.name.endswith(".mdc") else doc.name
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
            # No documents, use main content as index.mdc
            content = prompt.content
            if variables:
                for var_name, var_value in variables.items():
                    placeholder = "{{{ " + var_name + " }}}"
                    content = content.replace(placeholder, var_value)

            output_file = rules_dir / "index.mdc"

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

        # Generate plugin files for v2.1/v3.0
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            # Merge variables for plugins
            merged_vars = {}
            if prompt.variables:
                merged_vars.update(prompt.variables)
            if variables:
                merged_vars.update(variables)

            plugin_files = self._generate_plugins(
                prompt,
                output_dir,
                dry_run,
                verbose,
                merged_vars if merged_vars else None,
            )
            created_files.extend(plugin_files)

        return created_files

    def _generate_plugins(
        self,
        prompt: Union[UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate plugin files for Cursor (v2.1 and v3.0 compatible)."""
        created_files = []
        cursor_dir = output_dir / ".cursor"

        # Extract plugin data from either v3 top-level or v2.1 nested structure
        mcp_servers = None
        agents = None
        commands = None

        if isinstance(prompt, UniversalPromptV3):
            # V3: Check top-level fields
            mcp_servers = prompt.mcp_servers
            agents = prompt.agents
            commands = prompt.commands
        elif isinstance(prompt, UniversalPromptV2) and prompt.plugins:
            # V2.1: Use nested plugins structure (deprecated)
            if prompt.plugins.mcp_servers:
                click.echo(
                    DeprecationWarnings.v3_nested_plugin_field_warning("mcp_servers")
                )
                mcp_servers = prompt.plugins.mcp_servers
            if prompt.plugins.agents:
                click.echo(DeprecationWarnings.v3_nested_plugin_field_warning("agents"))
                agents = prompt.plugins.agents
            if prompt.plugins.commands:
                click.echo(
                    DeprecationWarnings.v3_nested_plugin_field_warning("commands")
                )
                commands = prompt.plugins.commands

        # Generate MCP server configurations
        if mcp_servers:
            mcp_file = cursor_dir / "mcp-servers.json"
            mcp_servers_config = {}
            for server in mcp_servers:
                server_config: Dict[str, Any] = {
                    "command": server.command,
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
                cursor_dir.mkdir(parents=True, exist_ok=True)
                with open(mcp_file, "w", encoding="utf-8") as f:
                    json.dump(mcp_config, f, indent=2)
                click.echo(f"✅ Generated: {mcp_file}")
            created_files.append(mcp_file)

        # Generate agent schemas
        if agents:
            schemas_dir = cursor_dir / "agent-schemas"
            for agent in agents:
                # Apply variable substitution
                agent_prompt = agent.system_prompt
                if variables:
                    for var_name, var_value in variables.items():
                        placeholder = "{{{ " + var_name + " }}}"
                        agent_prompt = agent_prompt.replace(placeholder, var_value)

                schema_file = schemas_dir / f"{agent.name}.json"
                agent_schema = {
                    "name": agent.name,
                    "description": agent.description,
                    "systemPrompt": agent_prompt,
                    "tools": agent.tools or [],
                    "trustLevel": agent.trust_level,
                    "requiresApproval": agent.requires_approval,
                    **({"context": agent.context} if agent.context else {}),
                }

                if dry_run:
                    click.echo(f"  📁 Would create: {schema_file}")
                    if verbose:
                        preview = json.dumps(agent_schema, indent=2)[:200] + "..."
                        click.echo(f"    {preview}")
                else:
                    schemas_dir.mkdir(parents=True, exist_ok=True)
                    with open(schema_file, "w", encoding="utf-8") as f:
                        json.dump(agent_schema, f, indent=2)
                    click.echo(f"✅ Generated: {schema_file}")
                created_files.append(schema_file)

        # Generate agent functions (tools available to agents)
        if commands:
            functions_dir = cursor_dir / "agent-functions"
            for command in commands:
                # Apply variable substitution
                command_prompt = command.prompt
                if variables:
                    for var_name, var_value in variables.items():
                        placeholder = "{{{ " + var_name + " }}}"
                        command_prompt = command_prompt.replace(placeholder, var_value)

                function_file = functions_dir / f"{command.name}.json"
                function_schema = {
                    "name": command.name,
                    "description": command.description,
                    "prompt": command_prompt,
                    **(
                        {"outputFormat": command.output_format}
                        if command.output_format
                        else {}
                    ),
                    "requiresApproval": command.requires_approval,
                }

                if dry_run:
                    click.echo(f"  📁 Would create: {function_file}")
                    if verbose:
                        preview = json.dumps(function_schema, indent=2)[:200] + "..."
                        click.echo(f"    {preview}")
                else:
                    functions_dir.mkdir(parents=True, exist_ok=True)
                    with open(function_file, "w", encoding="utf-8") as f:
                        json.dump(function_schema, f, indent=2)
                    click.echo(f"✅ Generated: {function_file}")
                created_files.append(function_file)

        return created_files

    def _generate_rules_system(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate modern .cursor/rules/ system with .mdc files."""
        # V2/V3 doesn't generate rules system
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            return []

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

    def _generate_index_file(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate main index.mdc file for project overview."""
        # V2/V3 uses simpler structure
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            return []

        rules_dir = output_dir / ".cursor" / "rules"
        index_file = rules_dir / "index.mdc"

        # Build index content for single prompt file
        index_content = self._build_single_index_content(prompt)

        if dry_run:
            click.echo(f"  📁 Would create: {index_file}")
            if verbose:
                preview = (
                    index_content[:200] + "..."
                    if len(index_content) > 200
                    else index_content
                )
                click.echo(f"    {preview}")
            return [index_file]
        else:
            rules_dir.mkdir(parents=True, exist_ok=True)
            with open(index_file, "w", encoding="utf-8") as f:
                f.write(index_content)
            click.echo(f"✅ Generated: {index_file}")
            return [index_file]

    def _generate_agents_file(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate AGENTS.md file for simple agent instructions."""
        # V2/V3 doesn't generate agents file
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            return []
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

    def generate_merged(
        self,
        prompt_files: List[
            tuple[Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3], Path]
        ],
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> List[Path]:
        """Generate merged Cursor rules from multiple prompt files using modern .mdc format."""
        created_files = []
        rules_dir = output_dir / ".cursor" / "rules"

        # Generate main index.mdc with merged project overview
        index_content = self._build_merged_index_content(prompt_files, variables)
        index_file = rules_dir / "index.mdc"

        if dry_run:
            click.echo(f"  📁 Would create merged: {index_file}")
            if verbose:
                click.echo("  📄 Merged project overview preview:")
                preview = (
                    index_content[:300] + "..."
                    if len(index_content) > 300
                    else index_content
                )
                click.echo(f"    {preview}")
            created_files.append(index_file)
        else:
            rules_dir.mkdir(parents=True, exist_ok=True)
            with open(index_file, "w", encoding="utf-8") as f:
                f.write(index_content)
            click.echo(
                f"✅ Generated merged project overview: {index_file} (from {len(prompt_files)} files)"
            )
            created_files.append(index_file)

        # Generate source-specific rules for each prompt file
        for i, (prompt, source_file) in enumerate(prompt_files):
            processed_prompt = self.substitute_variables(prompt, variables)
            source_rules = self._generate_source_specific_rules(
                processed_prompt, source_file, rules_dir, dry_run, verbose
            )
            created_files.extend(source_rules)

        return created_files

    def validate(
        self, prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]
    ) -> List[ValidationError]:
        """Validate prompt for Cursor."""
        errors = []

        # V2/V3 validation: check content exists
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            if not prompt.content or not prompt.content.strip():
                errors.append(
                    ValidationError(
                        field="content",
                        message="Cursor requires content",
                        severity="error",
                    )
                )
            return errors

        # V1 validation: Cursor works well with structured instructions
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
            "javascript": "**/*.{js,jsx,mjs,cjs}",
            "python": "**/*.{py,pyi}",
            "react": "**/*.{tsx,jsx}",
            "vue": "**/*.{vue,js,ts}",
            "angular": "**/*.{ts,js,html,scss,css}",
            "node": "**/*.{js,ts,mjs,cjs}",
            "go": "**/*.go",
            "rust": "**/*.{rs,toml}",
            "java": "**/*.{java,kt}",
            "kotlin": "**/*.{kt,kts}",
            "cpp": "**/*.{cpp,c,h,hpp,cc,cxx}",
            "c": "**/*.{c,h}",
            "csharp": "**/*.{cs,csx}",
            "php": "**/*.{php,phtml}",
            "ruby": "**/*.{rb,rake}",
            "swift": "**/*.swift",
            "scala": "**/*.{scala,sc}",
            "shell": "**/*.{sh,bash,zsh}",
            "docker": "**/Dockerfile*",
            "yaml": "**/*.{yml,yaml}",
            "json": "**/*.json",
            "html": "**/*.{html,htm}",
            "css": "**/*.{css,scss,sass,less}",
            "sql": "**/*.{sql,pgsql,mysql}",
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
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate Cursor ignore files for better indexing control."""
        # V2/V3 doesn't generate ignore files
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            return []
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

        # Technology-specific ignore patterns (avoid duplicates)
        if prompt.context and prompt.context.technologies:
            tech_categories = set()
            tech_lower_list = [tech.lower() for tech in prompt.context.technologies]

            # Determine which tech categories are present
            if any(
                tech in ["react", "typescript", "javascript", "node"]
                for tech in tech_lower_list
            ):
                tech_categories.add("javascript")
            if "python" in tech_lower_list:
                tech_categories.add("python")
            if any(tech in ["java", "kotlin"] for tech in tech_lower_list):
                tech_categories.add("java")

            # Add patterns for each category only once
            if "javascript" in tech_categories:
                lines.append("# JavaScript/Node.js specific")
                lines.append("coverage/")
                lines.append("*.tsbuildinfo")
                lines.append("npm-debug.log*")
                lines.append("")
            if "python" in tech_categories:
                lines.append("# Python specific")
                lines.append("*.egg-info/")
                lines.append(".pytest_cache/")
                lines.append(".coverage")
                lines.append(".mypy_cache/")
                lines.append("")
            if "java" in tech_categories:
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

    def _build_merged_content(
        self,
        prompt_files: List[
            tuple[Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3], Path]
        ],
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> str:
        """Build merged Cursor rules content from multiple prompt files."""
        lines = []

        # Header with summary
        lines.append("# AI Assistant Rules")
        lines.append("")
        lines.append(
            f"This document contains merged AI assistant rules from {len(prompt_files)} configuration files."
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

            # Instructions (V1 only)
            if (
                isinstance(processed_prompt, UniversalPrompt)
                and processed_prompt.instructions
            ):
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

    def _build_merged_index_content(
        self,
        prompt_files: List[
            tuple[Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3], Path]
        ],
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> str:
        """Build merged index.mdc content for main project overview."""
        lines = []

        # Get the first prompt for primary metadata
        primary_prompt, primary_file = prompt_files[0]
        processed_prompt = self.substitute_variables(primary_prompt, variables)

        # YAML frontmatter for "Always" rule type
        lines.append("---")
        lines.append("description: Project overview and core guidelines")
        lines.append("alwaysApply: true")
        lines.append("---")
        lines.append("")

        # Project overview
        lines.append(f"# {processed_prompt.metadata.title}")
        lines.append("")
        lines.append(processed_prompt.metadata.description)
        lines.append("")

        # Configuration sources
        if len(prompt_files) > 1:
            lines.append("## Configuration Sources")
            lines.append(
                f"This project uses {len(prompt_files)} prompt configuration files:"
            )
            lines.append("")
            for i, (prompt, source_file) in enumerate(prompt_files, 1):
                lines.append(f"{i}. **{prompt.metadata.title}** (`{source_file.name}`)")
            lines.append("")

        # Project context (V1 only)
        if isinstance(processed_prompt, UniversalPrompt) and processed_prompt.context:
            lines.append("## Project Context")
            if processed_prompt.context.project_type:
                lines.append(f"**Type:** {processed_prompt.context.project_type}")
            if processed_prompt.context.technologies:
                lines.append(
                    f"**Technologies:** {', '.join(processed_prompt.context.technologies)}"
                )
            if processed_prompt.context.description:
                lines.append("")
                lines.append("**Description:**")
                lines.append(processed_prompt.context.description)
            lines.append("")

        # Core instructions from all sources (V1 only)
        lines.append("## Core Guidelines")
        all_general_instructions: List[str] = []
        for prompt, _ in prompt_files:
            processed = self.substitute_variables(prompt, variables)
            if (
                isinstance(processed, UniversalPrompt)
                and processed.instructions
                and processed.instructions.general
            ):
                all_general_instructions.extend(processed.instructions.general)

        # Remove duplicates while preserving order
        seen = set()
        unique_instructions = []
        for instruction in all_general_instructions:
            if instruction not in seen:
                seen.add(instruction)
                unique_instructions.append(instruction)

        for instruction in unique_instructions:
            lines.append(f"- {instruction}")

        return "\n".join(lines)

    def _build_single_index_content(self, prompt: UniversalPrompt) -> str:
        """Build index.mdc content for a single prompt file."""
        lines = []

        # YAML frontmatter for "Always" rule type
        lines.append("---")
        lines.append("description: Project overview and core guidelines")
        lines.append("alwaysApply: true")
        lines.append("---")
        lines.append("")

        # Project overview
        lines.append(f"# {prompt.metadata.title}")
        lines.append("")
        lines.append(prompt.metadata.description)
        lines.append("")

        # Project context
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

        # Core instructions
        if prompt.instructions and prompt.instructions.general:
            lines.append("## Core Guidelines")
            for instruction in prompt.instructions.general:
                lines.append(f"- {instruction}")
            lines.append("")

        # Architecture guidance
        if prompt.instructions and prompt.instructions.architecture:
            lines.append("## Architecture")
            for instruction in prompt.instructions.architecture:
                lines.append(f"- {instruction}")
            lines.append("")

        return "\n".join(lines)

    def _generate_source_specific_rules(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        source_file: Path,
        rules_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate source-specific MDC rules for a prompt file."""
        # V2/V3 doesn't generate source-specific rules
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            return []
        created_files = []

        # Create a sanitized filename from the source file
        sanitized_name = source_file.stem.replace(".", "-").replace("_", "-")
        if sanitized_name.endswith("-promptrek"):
            sanitized_name = sanitized_name[:-10]  # Remove -promptrek suffix

        # Generate different rule types based on instruction categories
        instruction_data = (
            prompt.instructions.model_dump() if prompt.instructions else {}
        )

        for category, instructions in instruction_data.items():
            if instructions:  # Only generate files for non-empty categories
                rule_file = (
                    rules_dir / f"{sanitized_name}-{category.replace('_', '-')}.mdc"
                )
                rule_content = self._build_category_mdc_content(
                    category, instructions, prompt, source_file
                )

                if dry_run:
                    click.echo(f"  📁 Would create: {rule_file}")
                    if verbose:
                        preview = (
                            rule_content[:200] + "..."
                            if len(rule_content) > 200
                            else rule_content
                        )
                        click.echo(f"    {preview}")
                    created_files.append(rule_file)
                else:
                    with open(rule_file, "w", encoding="utf-8") as f:
                        f.write(rule_content)
                    click.echo(f"✅ Generated: {rule_file}")
                    created_files.append(rule_file)

        return created_files

    def _build_category_mdc_content(
        self,
        category: str,
        instructions: List[str],
        prompt: UniversalPrompt,
        source_file: Path,
    ) -> str:
        """Build MDC content for a specific instruction category."""
        lines = []

        # Determine rule type and globs based on category
        rule_config = self._get_rule_config_for_category(category, prompt)

        # YAML frontmatter
        lines.append("---")
        lines.append(f"description: {rule_config['description']}")
        if rule_config.get("globs"):
            lines.append(f'globs: "{rule_config["globs"]}"')
        lines.append(f"alwaysApply: {str(rule_config['always_apply']).lower()}")
        lines.append("---")
        lines.append("")

        # Content
        category_title = category.replace("_", " ").title()
        lines.append(f"# {category_title} Guidelines")
        lines.append("")
        lines.append(f"*Source: {source_file.name}*")
        lines.append("")

        for instruction in instructions:
            lines.append(f"- {instruction}")

        return "\n".join(lines)

    def _get_rule_config_for_category(
        self, category: str, prompt: UniversalPrompt
    ) -> Dict[str, Any]:
        """Get rule configuration (type, globs, etc.) for an instruction category."""
        # Default configuration
        config = {
            "description": f"{category.replace('_', ' ').title()} guidelines",
            "always_apply": False,
        }

        # Category-specific configurations
        if category == "general":
            config["description"] = "General coding guidelines"
            config["always_apply"] = True  # General rules always apply
        elif category == "code_style":
            config["description"] = "Code style and formatting guidelines"
            config["globs"] = "**/*.{py,js,ts,tsx,jsx,go,rs,java,cpp,c,h}"
        elif category == "testing":
            config["description"] = "Testing standards and practices"
            config["globs"] = "**/*.{test,spec}.{py,js,ts,tsx,jsx}"
        elif category == "architecture":
            config["description"] = "Architecture and design patterns"
            config["always_apply"] = True
        elif category == "security":
            config["description"] = "Security guidelines and best practices"
            config["always_apply"] = True
        elif category == "performance":
            config["description"] = "Performance optimization guidelines"
            config["globs"] = "**/*.{py,js,ts,tsx,jsx,go,rs,java,cpp,c,h}"
        else:
            # For custom categories, try to infer from technologies
            if prompt.context and prompt.context.technologies:
                main_tech = prompt.context.technologies[0].lower()
                tech_patterns = {
                    "python": "**/*.{py,pyi}",
                    "javascript": "**/*.{js,jsx,mjs,cjs}",
                    "typescript": "**/*.{ts,tsx}",
                    "react": "**/*.{tsx,jsx}",
                    "vue": "**/*.{vue,js,ts}",
                    "angular": "**/*.{ts,js,html,scss,css}",
                    "node": "**/*.{js,ts,mjs,cjs}",
                    "go": "**/*.go",
                    "rust": "**/*.{rs,toml}",
                    "java": "**/*.{java,kt}",
                    "kotlin": "**/*.{kt,kts}",
                    "cpp": "**/*.{cpp,c,h,hpp,cc,cxx}",
                    "c": "**/*.{c,h}",
                    "csharp": "**/*.{cs,csx}",
                    "php": "**/*.{php,phtml}",
                    "ruby": "**/*.{rb,rake}",
                    "swift": "**/*.swift",
                    "scala": "**/*.{scala,sc}",
                }
                if main_tech in tech_patterns:
                    config["globs"] = tech_patterns[main_tech]

        return config

    def parse_files(
        self, source_dir: Path
    ) -> Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]:
        """
        Parse Cursor files back into a UniversalPrompt, UniversalPromptV2, or UniversalPromptV3.

        Args:
            source_dir: Directory containing Cursor configuration files

        Returns:
            UniversalPrompt or UniversalPromptV2 object parsed from Cursor files
        """
        return self.parse_markdown_rules_files(
            source_dir=source_dir,
            rules_subdir=".cursor/rules",
            file_extension="mdc",
            editor_name="Cursor",
        )
