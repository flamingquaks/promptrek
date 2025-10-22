"""
Cline (VSCode AI coding assistant extension) adapter implementation.
"""

import platform
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import click

from ..core.exceptions import DeprecationWarnings, ValidationError
from ..core.models import (
    UniversalPrompt,
    UniversalPromptV2,
    UniversalPromptV3,
    UserConfig,
)
from .base import EditorAdapter
from .mcp_mixin import MCPGenerationMixin
from .sync_mixin import MarkdownSyncMixin


class ClineAdapter(MCPGenerationMixin, MarkdownSyncMixin, EditorAdapter):
    """Adapter for Cline VSCode AI coding assistant extension."""

    _description = "Cline VSCode Extension (.clinerules, .clinerules/*.md)"
    _file_patterns = [".clinerules", ".clinerules/*.md"]

    def __init__(self) -> None:
        super().__init__(
            name="cline",
            description=self._description,
            file_patterns=self._file_patterns,
        )

    @staticmethod
    def get_default_config_paths() -> List[Path]:
        """
        Get list of default paths to search for cline_mcp_settings.json.

        Returns:
            List of possible paths to check
        """
        system = platform.system()
        paths = []

        if system == "Darwin":  # macOS
            base_path = Path.home() / "Library" / "Application Support"
        elif system == "Windows":
            base_path = Path.home() / "AppData" / "Roaming"
        else:  # Linux and others
            base_path = Path.home() / ".config"

        # VS Code
        paths.append(
            base_path
            / "Code"
            / "User"
            / "globalStorage"
            / "saoudrizwan.claude-dev"
            / "settings"
            / "cline_mcp_settings.json"
        )

        # VS Code Insiders
        paths.append(
            base_path
            / "Code - Insiders"
            / "User"
            / "globalStorage"
            / "saoudrizwan.claude-dev"
            / "settings"
            / "cline_mcp_settings.json"
        )

        # Cursor (uses same extension ID)
        paths.append(
            base_path
            / "Cursor"
            / "User"
            / "globalStorage"
            / "saoudrizwan.claude-dev"
            / "settings"
            / "cline_mcp_settings.json"
        )

        return paths

    @staticmethod
    def find_mcp_config_file() -> Optional[Path]:
        """
        Try to find the cline_mcp_settings.json file in common locations.

        Returns:
            Path if found, None otherwise
        """
        for path in ClineAdapter.get_default_config_paths():
            if path.exists():
                return path
        return None

    @staticmethod
    def prompt_for_mcp_config_path() -> Optional[Path]:
        """
        Prompt user to provide the path to cline_mcp_settings.json.

        Returns:
            Path provided by user, or None if skipped
        """
        click.echo("\n❌ Could not find Cline MCP configuration file")
        click.echo("\nTo find your Cline MCP configuration file:")
        click.echo("  1. Open VS Code with Cline extension")
        click.echo("  2. Open Cline chat window")
        click.echo("  3. At the bottom, click the stacked servers icon (MCP)")
        click.echo("  4. Click the settings cog icon")
        click.echo('  5. Click "Configure MCP Servers"')
        click.echo("  6. Right-click on the file tab at the top")
        click.echo('  7. Click "Copy Path"')
        click.echo("  8. Paste the path below")
        click.echo("")

        path_str = click.prompt(
            "Enter path to cline_mcp_settings.json (or press Enter to skip)",
            default="",
            show_default=False,
        )

        if not path_str:
            return None

        path = Path(path_str).expanduser()
        if not path.exists():
            click.echo(f"⚠️  Warning: File does not exist: {path}")
            if not click.confirm("Use this path anyway?", default=False):
                return None

        return path

    @staticmethod
    def _find_user_config(output_dir: Path) -> Path:
        """
        Find or determine location for user-config.promptrek.yaml in .promptrek/ directory.

        Searches in order:
        1. .promptrek/user-config.promptrek.yaml in output_dir
        2. .promptrek/user-config.promptrek.yaml in current working directory
        3. Returns path in output_dir/.promptrek/ (even if it doesn't exist yet)

        Args:
            output_dir: Directory where files are being generated

        Returns:
            Path to .promptrek/user-config.promptrek.yaml file
        """
        # Try output_dir/.promptrek/ first
        user_config = output_dir / ".promptrek" / "user-config.promptrek.yaml"
        if user_config.exists():
            return user_config

        # Try current working directory/.promptrek/
        cwd = Path.cwd()
        user_config_cwd = cwd / ".promptrek" / "user-config.promptrek.yaml"
        if user_config_cwd.exists():
            return user_config_cwd

        # Default to output_dir/.promptrek/ (even if doesn't exist yet)
        return output_dir / ".promptrek" / "user-config.promptrek.yaml"

    @staticmethod
    def _read_user_config(user_config_path: Path) -> Optional[UserConfig]:
        """
        Read user config from user-config.promptrek.yaml.

        Args:
            user_config_path: Path to user-config.promptrek.yaml

        Returns:
            UserConfig object or None if file doesn't exist
        """
        if not user_config_path.exists():
            return None

        try:
            import yaml

            with open(user_config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data:
                return None

            return UserConfig(**data)
        except Exception:
            return None

    @staticmethod
    def _write_user_config(
        user_config_path: Path, mcp_config_path: Path, verbose: bool = False
    ) -> bool:
        """
        Write or update user config with Cline MCP path.

        Args:
            user_config_path: Path to user-config.promptrek.yaml
            mcp_config_path: Path to cline_mcp_settings.json
            verbose: Enable verbose output

        Returns:
            True if write was successful, False otherwise
        """
        try:
            # Read existing config or create new one
            user_config = ClineAdapter._read_user_config(user_config_path)

            if not user_config:
                user_config = UserConfig(
                    schema_version="1.0.0",
                    editor_paths={"cline_mcp_path": str(mcp_config_path)},
                )
            else:
                # Update existing config
                if not user_config.editor_paths:
                    user_config.editor_paths = {}
                user_config.editor_paths["cline_mcp_path"] = str(mcp_config_path)

            # Write to file with warning comments
            user_config_path.parent.mkdir(parents=True, exist_ok=True)

            import yaml

            with open(user_config_path, "w", encoding="utf-8") as f:
                # Add YAML language server directive for schema validation
                f.write(
                    "# yaml-language-server: $schema=https://promptrek.ai/schema/user-config/v1.0.0.json\n"
                )
                f.write("#\n")
                # Add warning comments
                f.write("# WARNING: This file contains user-specific configuration\n")
                f.write(
                    "# DO NOT commit this file to version control (it should be in .gitignore)\n"
                )
                f.write("#\n")
                f.write(
                    "# This file is automatically generated and contains paths specific to your machine.\n"
                )
                f.write(
                    "# Other developers will have different paths on their machines.\n"
                )
                f.write("\n")

                # Write YAML data
                yaml.safe_dump(
                    user_config.model_dump(exclude_none=True),
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                )

            # Add .promptrek/ directory to .gitignore
            ClineAdapter._add_to_gitignore(
                user_config_path.parent.parent, ".promptrek/"
            )

            click.echo(
                f"  💾 Saved Cline MCP path to: .promptrek/{user_config_path.name}"
            )
            if verbose:
                click.echo(f"     Path: {mcp_config_path}")

            return True

        except Exception as e:
            if verbose:
                click.echo(f"  ⚠️  Could not update user config: {e}")
            return False

    @staticmethod
    def _add_to_gitignore(project_dir: Path, pattern: str) -> None:
        """
        Add pattern to .gitignore if not already present.

        Args:
            project_dir: Project directory containing or to contain .gitignore
            pattern: Pattern to add to .gitignore
        """
        gitignore_path = project_dir / ".gitignore"

        # Check if .gitignore exists
        if gitignore_path.exists():
            # Read existing content
            try:
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check if pattern already exists
                if pattern in content:
                    return

                # Add pattern to existing file
                with open(gitignore_path, "a", encoding="utf-8") as f:
                    # Ensure file ends with newline before adding
                    if content and not content.endswith("\n"):
                        f.write("\n")
                    f.write("\n# PrompTrek user-specific config (not committed)\n")
                    f.write(f"{pattern}\n")

                click.echo(f"  📝 Added {pattern} to .gitignore")
            except Exception as e:
                click.echo(f"  ⚠️  Could not update .gitignore: {e}", err=True)
        else:
            # Create new .gitignore with pattern
            try:
                with open(gitignore_path, "w", encoding="utf-8") as f:
                    f.write("# PrompTrek user-specific config (not committed)\n")
                    f.write(f"{pattern}\n")
                click.echo(f"  📝 Created .gitignore and added {pattern}")
            except Exception as e:
                click.echo(f"  ⚠️  Could not create .gitignore: {e}", err=True)

    def get_mcp_config_strategy(self) -> Dict[str, Any]:
        """Get MCP configuration strategy for Cline adapter."""
        return {
            "supports_project": False,  # Cline only supports user-level MCP config
            "project_path": None,
            "system_path": None,  # Will be determined at runtime
            "requires_confirmation": True,  # Always confirm user-level changes
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
        """Generate Cline rules files - supports both single file and directory formats."""

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

        # Determine generation mode based on project size/complexity
        use_directory_format = self._should_use_directory_format(processed_prompt)

        if use_directory_format:
            # Generate multiple files in .clinerules/ directory
            created_files = self._generate_directory_format(
                processed_prompt, conditional_content, output_dir, dry_run, verbose
            )
        else:
            # Generate single .clinerules file
            created_files = self._generate_single_file_format(
                processed_prompt, conditional_content, output_dir, dry_run, verbose
            )

        return created_files

    def _generate_v2(
        self,
        prompt: Union[UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate Cline files from v2/v3 schema (using documents for multi-file or content for single file)."""
        created_files = []

        # If documents field is present, generate directory format with separate files
        if prompt.documents:
            clinerules_dir = output_dir / ".clinerules"
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
                output_file = clinerules_dir / filename

                if dry_run:
                    click.echo(f"  📁 Would create: {output_file}")
                    if verbose:
                        preview = (
                            content[:200] + "..." if len(content) > 200 else content
                        )
                        click.echo(f"    {preview}")
                    created_files.append(output_file)
                else:
                    clinerules_dir.mkdir(parents=True, exist_ok=True)
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    click.echo(f"✅ Generated: {output_file}")
                    created_files.append(output_file)
        else:
            # No documents, use main content as single .clinerules file
            content = prompt.content
            if variables:
                for var_name, var_value in variables.items():
                    placeholder = "{{{ " + var_name + " }}}"
                    content = content.replace(placeholder, var_value)

            output_file = output_dir / ".clinerules"

            if dry_run:
                click.echo(f"  📁 Would create: {output_file}")
                if verbose:
                    preview = content[:200] + "..." if len(content) > 200 else content
                    click.echo(f"    {preview}")
                created_files.append(output_file)
            else:
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
        """Generate Cline files from v2.1/v3.0 schema with plugin support."""
        created_files = []

        # First, generate the regular v2/v3 markdown files
        markdown_files = self._generate_v2(
            prompt, output_dir, dry_run, verbose, variables
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
                prompt,
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
        prompt: Optional[Union[UniversalPromptV2, UniversalPromptV3]] = None,
    ) -> List[Path]:
        """Generate MCP configuration for Cline at user-level."""
        created_files: List[Path] = []

        # Step 1: Determine MCP config file location
        mcp_config_path: Optional[Path] = None
        path_was_discovered = False  # Track if we discovered (not configured) the path

        # Check if path is stored in user config
        user_config_file = self._find_user_config(output_dir)
        user_config = self._read_user_config(user_config_file)

        if (
            user_config
            and user_config.editor_paths
            and "cline_mcp_path" in user_config.editor_paths
        ):
            mcp_config_path = Path(
                user_config.editor_paths["cline_mcp_path"]
            ).expanduser()
            if verbose:
                click.echo(f"  ℹ️  Using configured Cline MCP path: {mcp_config_path}")

        # Try to find it automatically
        if not mcp_config_path:
            mcp_config_path = self.find_mcp_config_file()
            if mcp_config_path:
                path_was_discovered = True
                if verbose:
                    click.echo(f"  ✅ Found Cline MCP config: {mcp_config_path}")

        # Prompt user if not found
        if not mcp_config_path and not dry_run:
            mcp_config_path = self.prompt_for_mcp_config_path()
            if not mcp_config_path:
                click.echo("  ⏭️  Skipped Cline MCP configuration (no path provided)")
                return created_files
            path_was_discovered = True

        # If still no path (dry run mode), use a placeholder
        if not mcp_config_path:
            click.echo("  ⏭️  Skipped Cline MCP configuration (no path available)")
            return created_files

        # Save discovered path to user-config.promptrek.yaml (if it was auto-detected or user-provided)
        if path_was_discovered and not dry_run:
            self._write_user_config(user_config_file, mcp_config_path, verbose)

        # Build MCP servers config (uses standard MCP format)
        mcp_config = self.build_mcp_servers_config(
            mcp_servers, variables, format_style="standard"
        )
        new_servers = mcp_config.get("mcpServers", {})

        # Step 1: Show warning about user-level operations
        if not self.warn_user_level_operations(
            editor_name="Cline",
            config_path=mcp_config_path,
            server_count=len(new_servers),
            dry_run=dry_run,
        ):
            click.echo("  ⏭️  Skipped Cline MCP configuration")
            return created_files

        # Step 2: Read existing user-level config
        existing_config = self.read_existing_mcp_config(mcp_config_path)

        if existing_config:
            # Step 3: Detect conflicts (same name, different config)
            conflicts = self.detect_conflicting_servers(new_servers, existing_config)

            if conflicts:
                if verbose:
                    click.echo(f"  ⚠️  Found {len(conflicts)} conflicting MCP server(s)")

                # Step 4: Prompt for each conflict
                servers_to_skip = []
                existing_servers = existing_config.get("mcpServers", {})

                for server_name in conflicts:
                    if not self.prompt_mcp_server_overwrite(
                        server_name=server_name,
                        existing_config=existing_servers[server_name],
                        new_config=new_servers[server_name],
                        dry_run=dry_run,
                    ):
                        servers_to_skip.append(server_name)
                        if verbose:
                            click.echo(
                                f"  ⏭️  Skipping MCP server '{server_name}' (keeping existing)"
                            )

                # Remove servers user chose to skip
                for server_name in servers_to_skip:
                    del new_servers[server_name]

            # Step 5: Merge with existing config (add/update only)
            if verbose:
                click.echo("  ℹ️  Merging MCP servers with existing user-level config")

            merged_config = existing_config.copy()
            if "mcpServers" not in merged_config:
                merged_config["mcpServers"] = {}
            merged_config["mcpServers"].update(new_servers)
        else:
            # No existing config, create new
            merged_config = mcp_config

        # Step 6: Write the config file
        if new_servers:  # Only write if we have servers to add
            if self.write_mcp_config_file(
                merged_config, mcp_config_path, dry_run, verbose
            ):
                created_files.append(mcp_config_path)
                if not dry_run:
                    click.echo(
                        f"  ✅ Updated {len(new_servers)} MCP server(s) at user-level"
                    )
        else:
            click.echo("  ℹ️  No MCP servers to add (all skipped)")

        return created_files

    def validate(
        self, prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]
    ) -> List[ValidationError]:
        """Validate prompt for Cline."""
        errors = []

        # V2/V3 validation: check content exists
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            if not prompt.content or not prompt.content.strip():
                errors.append(
                    ValidationError(
                        field="content",
                        message="Cline requires content",
                        severity="error",
                    )
                )
            return errors

        # V1 validation: Cline works well with clear instructions and context
        if not prompt.instructions or not prompt.instructions.general:
            errors.append(
                ValidationError(
                    field="instructions.general",
                    message=("Cline needs clear general instructions for coding tasks"),
                )
            )

        # Validate that we have meaningful content to generate rules
        if not prompt.metadata or not prompt.metadata.title:
            errors.append(
                ValidationError(
                    field="metadata.title",
                    message=("Cline rules need a clear project title"),
                )
            )

        return errors

    def supports_variables(self) -> bool:
        """Cline supports variable substitution."""
        return True

    def supports_conditionals(self) -> bool:
        """Cline supports conditional configuration."""
        return True

    def parse_files(
        self, source_dir: Path
    ) -> Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]:
        """Parse Cline files back into a UniversalPrompt, UniversalPromptV2, or UniversalPromptV3."""
        return self.parse_markdown_rules_files(
            source_dir=source_dir,
            rules_subdir=".clinerules",
            file_extension="md",
            editor_name="Cline",
        )

    def _generate_rule_files(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """Generate multiple rule files for modular organization."""
        rule_files = {}

        # 1. Main project overview file
        rule_files["01-project-overview.md"] = self._build_project_overview(prompt)

        # 2. Coding guidelines file
        coding_content = self._build_coding_guidelines(prompt, conditional_content)
        if coding_content:
            rule_files["02-coding-guidelines.md"] = coding_content

        # 3. Code style file
        style_content = self._build_code_style(prompt)
        if style_content:
            rule_files["03-code-style.md"] = style_content

        # 4. Testing standards file
        testing_content = self._build_testing_standards(prompt)
        if testing_content:
            rule_files["04-testing-standards.md"] = testing_content

        # 5. Examples file
        examples_content = self._build_examples(prompt)
        if examples_content:
            rule_files["05-examples.md"] = examples_content

        return rule_files

    def _build_project_overview(self, prompt: UniversalPrompt) -> str:
        """Build project overview content."""
        lines = []

        # Header
        lines.append(f"# {prompt.metadata.title}")
        lines.append("")
        lines.append("## Project Overview")
        lines.append(prompt.metadata.description)
        lines.append("")

        # Project Information
        if prompt.context:
            lines.append("## Project Context")
            if prompt.context.project_type:
                lines.append(f"- **Project Type:** {prompt.context.project_type}")
            if prompt.context.technologies:
                lines.append(
                    f"- **Technologies:** {', '.join(prompt.context.technologies)}"
                )
            if prompt.context.description:
                lines.append(f"- **Details:** {prompt.context.description}")
            lines.append("")

        return "\n".join(lines)

    def _build_coding_guidelines(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build coding guidelines content."""
        lines = []

        # Collect all instructions (original + conditional)
        all_general_instructions = []
        if prompt.instructions and prompt.instructions.general:
            all_general_instructions.extend(prompt.instructions.general)

        # Add conditional general instructions
        if (
            conditional_content
            and "instructions" in conditional_content
            and "general" in conditional_content["instructions"]
        ):
            all_general_instructions.extend(
                conditional_content["instructions"]["general"]
            )

        # General instructions
        if all_general_instructions:
            lines.append("# Coding Guidelines")
            lines.append("")
            lines.append("## General Instructions")
            for instruction in all_general_instructions:
                lines.append(f"- {instruction}")
            lines.append("")

        return "\n".join(lines) if lines else ""

    def _build_code_style(self, prompt: UniversalPrompt) -> str:
        """Build code style content."""
        lines = []

        # Code style instructions
        if prompt.instructions and prompt.instructions.code_style:
            lines.append("# Code Style Guidelines")
            lines.append("")
            lines.append("## Style Rules")
            for guideline in prompt.instructions.code_style:
                lines.append(f"- {guideline}")
            lines.append("")

        return "\n".join(lines) if lines else ""

    def _build_testing_standards(self, prompt: UniversalPrompt) -> str:
        """Build testing standards content."""
        lines = []

        # Testing instructions if available
        if (
            prompt.instructions
            and hasattr(prompt.instructions, "testing")
            and prompt.instructions.testing
        ):
            lines.append("# Testing Standards")
            lines.append("")
            lines.append("## Testing Requirements")
            for test_rule in prompt.instructions.testing:
                lines.append(f"- {test_rule}")
            lines.append("")

        return "\n".join(lines) if lines else ""

    def _build_examples(self, prompt: UniversalPrompt) -> str:
        """Build examples content."""
        lines = []

        # Examples if available
        if prompt.examples:
            lines.append("# Code Examples")
            lines.append("")
            for name, example in prompt.examples.items():
                lines.append(f"## {name.replace('_', ' ').title()}")
                lines.append("```")
                lines.append(example)
                lines.append("```")
                lines.append("")

        return "\n".join(lines) if lines else ""

    def _should_use_directory_format(
        self, prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]
    ) -> bool:
        """Determine if directory format should be used based on complexity."""
        # V2/V3 uses single file format
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            return False

        complexity_score = 0

        # Count different types of content (V1 only)
        if prompt.instructions and prompt.instructions.general:
            complexity_score += len(prompt.instructions.general)
        if prompt.instructions and prompt.instructions.code_style:
            complexity_score += len(prompt.instructions.code_style)
        if (
            prompt.instructions
            and hasattr(prompt.instructions, "testing")
            and prompt.instructions.testing
        ):
            complexity_score += len(prompt.instructions.testing)
        if prompt.examples:
            complexity_score += len(prompt.examples)

        # Use directory format for complex projects (>8 items) or multiple categories
        has_multiple_categories = (
            sum(
                [
                    bool(prompt.instructions and prompt.instructions.general),
                    bool(prompt.instructions and prompt.instructions.code_style),
                    bool(
                        prompt.instructions
                        and hasattr(prompt.instructions, "testing")
                        and prompt.instructions.testing
                    ),
                    bool(prompt.examples),
                ]
            )
            > 2
        )

        return complexity_score > 8 or has_multiple_categories

    def _generate_directory_format(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        conditional_content: Optional[Dict[str, Any]],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate multiple files in .clinerules/ directory."""
        # V2/V3 shouldn't reach here (uses single file), but handle it anyway
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            return self._generate_single_file_format(
                prompt, conditional_content, output_dir, dry_run, verbose
            )

        clinerules_dir = output_dir / ".clinerules"
        created_files = []

        # Generate multiple rule files based on content (V1 only)
        rule_files = self._generate_rule_files(prompt, conditional_content)

        if dry_run:
            click.echo(f"  📁 Would create directory: {clinerules_dir}")
            for filename, content in rule_files.items():
                output_file = clinerules_dir / filename
                click.echo(f"  📄 Would create: {output_file}")
                if verbose:
                    click.echo("      Content preview:")
                    preview = content[:200] + "..." if len(content) > 200 else content
                    click.echo(f"      {preview}")
                created_files.append(output_file)
        else:
            # Create .clinerules directory if it doesn't exist
            clinerules_dir.mkdir(parents=True, exist_ok=True)

            # Create rule files
            for filename, content in rule_files.items():
                output_file = clinerules_dir / filename
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(content)
                click.echo(f"✅ Generated: {output_file}")
                created_files.append(output_file)

        return created_files

    def _generate_single_file_format(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        conditional_content: Optional[Dict[str, Any]],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate single .clinerules file."""
        output_file = output_dir / ".clinerules"

        # For V2/V3, use content directly
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            content = prompt.content
        else:
            # Create unified content for single file (V1)
            content = self._build_unified_content(prompt, conditional_content)

        if dry_run:
            click.echo(f"  📄 Would create: {output_file}")
            if verbose:
                click.echo("      Content preview:")
                preview = content[:200] + "..." if len(content) > 200 else content
                click.echo(f"      {preview}")
        else:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"✅ Generated: {output_file}")

        return [output_file]

    def _build_unified_content(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build unified content for single .clinerules file."""
        lines = []

        # Header
        lines.append(f"# {prompt.metadata.title}")
        lines.append("")
        lines.append("## Project Overview")
        lines.append(prompt.metadata.description)
        lines.append("")

        # Project Information
        if prompt.context:
            lines.append("## Project Context")
            if prompt.context.project_type:
                lines.append(f"- **Project Type:** {prompt.context.project_type}")
            if prompt.context.technologies:
                lines.append(
                    f"- **Technologies:** {', '.join(prompt.context.technologies)}"
                )
            if prompt.context.description:
                lines.append(f"- **Details:** {prompt.context.description}")
            lines.append("")

        # Collect all instructions (original + conditional)
        all_general_instructions = []
        if prompt.instructions and prompt.instructions.general:
            all_general_instructions.extend(prompt.instructions.general)

        # Add conditional general instructions
        if (
            conditional_content
            and "instructions" in conditional_content
            and "general" in conditional_content["instructions"]
        ):
            all_general_instructions.extend(
                conditional_content["instructions"]["general"]
            )

        # General instructions
        if all_general_instructions:
            lines.append("## Coding Guidelines")
            for instruction in all_general_instructions:
                lines.append(f"- {instruction}")
            lines.append("")

        # Code style instructions
        if prompt.instructions and prompt.instructions.code_style:
            lines.append("## Code Style")
            for guideline in prompt.instructions.code_style:
                lines.append(f"- {guideline}")
            lines.append("")

        # Testing instructions if available
        if (
            prompt.instructions
            and hasattr(prompt.instructions, "testing")
            and prompt.instructions.testing
        ):
            lines.append("## Testing Standards")
            for test_rule in prompt.instructions.testing:
                lines.append(f"- {test_rule}")
            lines.append("")

        # Examples if available
        if prompt.examples:
            lines.append("## Code Examples")
            lines.append("")
            for name, example in prompt.examples.items():
                lines.append(f"### {name.replace('_', ' ').title()}")
                lines.append("```")
                lines.append(example)
                lines.append("```")
                lines.append("")

        return "\n".join(lines)
