"""
Variable substitution utilities for PromptTrek.

Handles variable replacement in templates and UPF content.
Supports both static and dynamic (command-based) variables.
"""

import os
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Match, Optional

import yaml

from ..core.exceptions import TemplateError
from ..core.models import UniversalPrompt


class CommandExecutor:
    """Executes shell commands with security controls for dynamic variables."""

    def __init__(
        self, allow_commands: bool = False, timeout: int = 5, verbose: bool = False
    ) -> None:
        """
        Initialize command executor.

        Args:
            allow_commands: Whether to allow command execution (security control)
            timeout: Maximum command execution time in seconds
            verbose: Whether to show verbose output
        """
        self.allow_commands = allow_commands
        self.timeout = timeout
        self.verbose = verbose
        self._warned = False

    def execute(self, command: str) -> str:
        """
        Execute a shell command and return its output.

        WARNING: This executes user-defined commands. Only use with trusted input.
        Commands are executed via shell to support pipes, redirects, and environment variables.
        The allow_commands flag provides an additional security control.

        Args:
            command: Shell command to execute

        Returns:
            Command output as string (stripped of whitespace)

        Raises:
            TemplateError: If command execution is disabled or command fails
        """
        if not self.allow_commands:
            raise TemplateError(
                "Command execution is disabled. "
                "Set 'allow_commands: true' in project.promptrek.yaml to enable dynamic variables."
            )

        # Show security warning on first use
        if not self._warned and sys.stdout.isatty():
            self._show_warning()
            self._warned = True

        try:
            if self.verbose:
                print(f"  🔧 Executing: {command}")

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=True,
            )

            output = result.stdout.strip()

            if self.verbose and output:
                print(f"  ✅ Result: {output}")

            return output

        except subprocess.TimeoutExpired as e:
            raise TemplateError(
                f"Command timed out after {self.timeout}s: {command}"
            ) from e
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed with exit code {e.returncode}: {command}"
            if e.stderr:
                error_msg += f"\nError output: {e.stderr.strip()}"
            raise TemplateError(error_msg) from e
        except FileNotFoundError as e:
            raise TemplateError(
                f"Command not found: {command}\n"
                "Ensure the command is installed and available in PATH."
            ) from e
        except Exception as e:
            raise TemplateError(f"Failed to execute command: {command}\n{e}") from e

    def _show_warning(self) -> None:
        """Show security warning about command execution."""
        print(
            "\n⚠️  WARNING: Dynamic variables with command execution enabled\n"
            "   Commands defined in .promptrek/variables.promptrek.yaml will be executed.\n"
            "   Only use trusted variable files. Review all commands before running.\n"
        )


class DynamicVariable:
    """
    Represents a dynamic variable that evaluates at runtime via command execution.

    SECURITY WARNING: This class executes shell commands defined in variable files.
    Only use with trusted input. Commands are executed with shell=True to support
    shell features (pipes, environment variables, etc.). The CommandExecutor provides
    protection via the allow_commands flag (disabled by default) and user warnings.
    """

    def __init__(self, name: str, command: str, cache: bool = False) -> None:
        """
        Initialize dynamic variable.

        Args:
            name: Variable name
            command: Shell command to execute (ensure this comes from trusted source)
            cache: Whether to cache the result (evaluate once)

        Security Note:
            The command will be executed via shell. Only use commands from trusted
            variable files under your control.
        """
        self.name = name
        self.command = command
        self.cache = cache
        self._cached_value: Optional[str] = None

    def evaluate(self, executor: CommandExecutor) -> str:
        """
        Evaluate the variable by executing its command.

        Args:
            executor: Command executor instance (controls security via allow_commands)

        Returns:
            Variable value (command output)

        Raises:
            TemplateError: If command execution fails or is disabled

        Security Note:
            This method executes the shell command associated with this variable.
            Ensure the command comes from a trusted source.
        """
        if self.cache and self._cached_value is not None:
            return self._cached_value

        value = executor.execute(self.command)

        if self.cache:
            self._cached_value = value

        return value

    def clear_cache(self) -> None:
        """Clear cached value."""
        self._cached_value = None


class BuiltInVariables:
    """Provides standard built-in dynamic variables."""

    @staticmethod
    def get_all(verbose: bool = False) -> Dict[str, str]:
        """
        Get all built-in variables with their current values.

        Args:
            verbose: Whether to show verbose output

        Returns:
            Dictionary of built-in variable names and values
        """
        now = datetime.now()

        variables = {
            # Date/Time variables
            "CURRENT_DATE": now.strftime("%Y-%m-%d"),
            "CURRENT_TIME": now.strftime("%H:%M:%S"),
            "CURRENT_DATETIME": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "CURRENT_YEAR": now.strftime("%Y"),
            "CURRENT_MONTH": now.strftime("%m"),
            "CURRENT_DAY": now.strftime("%d"),
            # Project context variables
            "PROJECT_NAME": BuiltInVariables._get_project_name(verbose),
            "PROJECT_ROOT": str(Path.cwd().resolve()),
        }

        # Git variables (only if in git repo)
        git_vars = BuiltInVariables._get_git_variables(verbose)
        variables.update(git_vars)

        return variables

    @staticmethod
    def _get_project_name(verbose: bool = False) -> str:
        """
        Get project name from git repository or fallback to directory name.

        Tries to get the repository name from git remote URL.
        Falls back to current directory name if not in git repo.

        Args:
            verbose: Whether to show verbose output

        Returns:
            Project name as string
        """
        try:
            # Check if in git repo
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )

            if result.returncode == 0:
                # Try to get repository name from remote URL
                remote_result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    check=False,
                )

                if remote_result.returncode == 0:
                    remote_url = remote_result.stdout.strip()
                    # Extract repo name from URL
                    # Examples:
                    # https://github.com/user/repo.git -> repo
                    # git@github.com:user/repo.git -> repo
                    # /path/to/repo.git -> repo
                    if remote_url:
                        # Remove .git suffix if present
                        if remote_url.endswith(".git"):
                            remote_url = remote_url[:-4]
                        # Get last path component
                        repo_name = remote_url.rstrip("/").split("/")[-1]
                        # Handle git@host:user/repo format
                        if ":" in repo_name and "/" in repo_name.split(":")[-1]:
                            repo_name = repo_name.split(":")[-1].split("/")[-1]

                        if repo_name and verbose:
                            print(f"  📦 Using git repository name: {repo_name}")
                        return repo_name

        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            FileNotFoundError,
        ):
            pass

        # Fallback to current directory name
        dir_name = Path.cwd().name
        if verbose:
            print(f"  📁 Using directory name: {dir_name}")
        return dir_name

    @staticmethod
    def _get_git_variables(verbose: bool = False) -> Dict[str, str]:
        """
        Get git-related variables if in a git repository.

        Args:
            verbose: Whether to show verbose output

        Returns:
            Dictionary of git variables (empty if not in git repo)
        """
        variables = {}

        try:
            # Check if in git repo
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )

            if result.returncode == 0:
                # Get current branch
                branch_result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    check=True,
                )
                variables["GIT_BRANCH"] = branch_result.stdout.strip()

                # Get short commit hash
                commit_result = subprocess.run(
                    ["git", "rev-parse", "--short", "HEAD"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    check=True,
                )
                variables["GIT_COMMIT_SHORT"] = commit_result.stdout.strip()

        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            FileNotFoundError,
        ):
            # Not in git repo or git not available
            if verbose:
                print("  ℹ️  Git variables not available (not in git repository)")

        return variables


class VariableSubstitution:
    """Handles variable substitution in templates and content."""

    LOCAL_VARIABLES_FILE = ".promptrek/variables.promptrek.yaml"

    def __init__(self) -> None:
        """Initialize variable substitution system."""
        self.variable_pattern = re.compile(r"\{\{\{\s*(\w+)\s*\}\}\}")
        self.env_pattern = re.compile(r"\$\{(\w+)\}")

    def substitute(
        self,
        content: str,
        variables: Dict[str, Any],
        env_variables: bool = True,
        strict: bool = False,
    ) -> str:
        """
        Substitute variables in content.

        Args:
            content: The content to process
            variables: Dictionary of variable values
            env_variables: Whether to substitute environment variables
            strict: If True, raise error for undefined variables

        Returns:
            Content with variables substituted

        Raises:
            TemplateError: If strict mode and undefined variables found
        """
        result = content

        # Substitute template variables (e.g., {{{ VARIABLE_NAME }}})
        result = self._substitute_template_variables(result, variables, strict)

        # Substitute environment variables (e.g., ${VAR_NAME})
        if env_variables:
            result = self._substitute_env_variables(result, strict)

        return result

    def substitute_prompt(
        self,
        prompt: UniversalPrompt,
        additional_variables: Optional[Dict[str, Any]] = None,
        env_variables: bool = True,
        strict: bool = False,
    ) -> UniversalPrompt:
        """
        Create a copy of the prompt with all variables substituted.

        Args:
            prompt: The universal prompt to process
            additional_variables: Additional variables to merge with prompt variables
            env_variables: Whether to substitute environment variables
            strict: If True, raise error for undefined variables

        Returns:
            New UniversalPrompt with variables substituted
        """
        # Combine variables from prompt and additional variables
        variables = prompt.variables.copy() if prompt.variables else {}
        if additional_variables:
            variables.update(additional_variables)

        # Create a copy of the prompt data using aliases for proper reconstruction
        prompt_dict = prompt.model_dump(by_alias=True)

        # Substitute variables in all string fields recursively
        prompt_dict = self._substitute_dict_recursive(
            prompt_dict, variables, env_variables, strict
        )

        # Create a new prompt instance with substituted values
        return UniversalPrompt.model_validate(prompt_dict)

    def get_undefined_variables(
        self, content: str, variables: Dict[str, Any]
    ) -> List[str]:
        """
        Get list of undefined variables in content.

        Args:
            content: Content to analyze
            variables: Available variables

        Returns:
            List of undefined variable names
        """
        undefined = []

        # Check template variables
        for match in self.variable_pattern.finditer(content):
            var_name = match.group(1)
            if var_name not in variables:
                undefined.append(var_name)

        return list(set(undefined))

    def extract_variables(self, content: str) -> List[str]:
        """
        Extract all variable names from content.

        Args:
            content: Content to analyze

        Returns:
            List of variable names found
        """
        variables = []

        # Extract template variables
        for match in self.variable_pattern.finditer(content):
            variables.append(match.group(1))

        # Extract environment variables
        for match in self.env_pattern.finditer(content):
            variables.append(f"${{{match.group(1)}}}")

        return list(set(variables))

    def restore_variables_in_content(
        self,
        original_content: str,
        parsed_content: str,
        source_dir: Optional[Path] = None,
        verbose: bool = False,
    ) -> str:
        """
        Restore variable references in parsed content by comparing with original.

        During generation, variables like {{{ PROJECT_NAME }}} are replaced with
        their values. During sync, we want to restore these variable references
        to prevent variable loss.

        Algorithm:
        1. Extract variables from original content
        2. Evaluate those variables to get their current values
        3. Replace values in parsed content with variable placeholders,
           but only if the placeholder existed in the original

        Args:
            original_content: Original content with variable placeholders
            parsed_content: Parsed content with evaluated variable values
            source_dir: Source directory for loading variables (defaults to cwd)
            verbose: Whether to print restoration details

        Returns:
            Content with variables restored
        """
        if not original_content or not parsed_content:
            return parsed_content

        # Extract variable placeholders from original
        var_names = self.extract_variables(original_content)

        if not var_names:
            return parsed_content

        # Load and evaluate variables
        try:
            all_variables = self.load_and_evaluate_variables(
                search_dir=source_dir,
                allow_commands=True,
                include_builtins=True,
                verbose=False,
                clear_cache=False,
            )
        except Exception:
            # If we can't load variables, return parsed content as-is
            return parsed_content

        # Build replacement list: (value, placeholder, var_name)
        replacements = []

        for var_name in var_names:
            # Check if it's an environment variable
            if var_name.startswith("${") and var_name.endswith("}"):
                # Environment variable like ${HOME}
                env_var_name = var_name[2:-1]  # Extract HOME from ${HOME}
                env_value = os.getenv(env_var_name)
                if env_value:
                    replacements.append((env_value, var_name, var_name))
            else:
                # Template variable like {{{ PROJECT_NAME }}}
                if var_name in all_variables:
                    value = str(all_variables[var_name])
                    placeholder = f"{{{{{{ {var_name} }}}}}}"
                    replacements.append((value, placeholder, var_name))

        if not replacements:
            return parsed_content

        # Sort by value length (longest first) to handle overlapping values
        # This prevents "My Project" from being replaced before "My Project Name"
        replacements.sort(key=lambda x: len(x[0]), reverse=True)

        # Apply replacements
        restored_content = parsed_content
        restored_vars = []

        for value, placeholder, var_name in replacements:
            if not value:  # Skip empty values
                continue

            # Only restore if:
            # 1. The placeholder exists in original content
            # 2. The value exists in parsed content
            # 3. The placeholder doesn't already exist in parsed content
            if (
                placeholder in original_content
                and value in restored_content
                and placeholder not in restored_content
            ):
                count = restored_content.count(value)
                restored_content = restored_content.replace(value, placeholder)

                # Track what we restored for verbose output
                if count > 0:
                    restored_vars.append((var_name, count))

        # Print restoration summary if verbose
        if verbose and restored_vars:
            import click

            click.echo("  Variables restored in content:")
            for var_name, count in restored_vars:
                click.echo(f"    {var_name}: {count} occurrence(s)")

        return restored_content

    def _substitute_template_variables(
        self, content: str, variables: Dict[str, Any], strict: bool
    ) -> str:
        """Substitute template variables in content."""

        def replace_var(match: Match[str]) -> str:
            var_name = match.group(1)
            if var_name in variables:
                return str(variables[var_name])
            elif strict:
                raise TemplateError(f"Undefined variable: {var_name}")
            else:
                return match.group(0)  # Leave unchanged

        return self.variable_pattern.sub(replace_var, content)

    def _substitute_env_variables(self, content: str, strict: bool) -> str:
        """Substitute environment variables in content."""

        def replace_env(match: Match[str]) -> str:
            var_name = match.group(1)
            value = os.getenv(var_name)
            if value is not None:
                return value
            elif strict:
                raise TemplateError(f"Undefined environment variable: {var_name}")
            else:
                return match.group(0)  # Leave unchanged

        return self.env_pattern.sub(replace_env, content)

    def _substitute_dict_recursive(
        self, data: Any, variables: Dict[str, Any], env_variables: bool, strict: bool
    ) -> Any:
        """Recursively substitute variables in a dictionary/list structure."""
        if isinstance(data, str):
            return self.substitute(data, variables, env_variables, strict)
        elif isinstance(data, dict):
            return {
                k: self._substitute_dict_recursive(v, variables, env_variables, strict)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [
                self._substitute_dict_recursive(item, variables, env_variables, strict)
                for item in data
            ]
        else:
            return data

    def load_local_variables(self, search_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Load variables from local .promptrek/variables.promptrek.yaml file.

        Searches for .promptrek/variables.promptrek.yaml starting from search_dir
        (or current directory) and walking up parent directories.

        Also checks for deprecated location (variables.promptrek.yaml in root) and
        offers to migrate it to the new location.

        NOTE: This method returns static variables only. Use load_and_evaluate_variables()
        for dynamic variable support.

        Args:
            search_dir: Directory to start search from (defaults to current dir)

        Returns:
            Dictionary of static variables loaded from file, empty dict if not found
        """
        start_dir = search_dir if search_dir else Path.cwd()

        # Search current directory and parents
        current = start_dir.resolve()
        while True:
            # Check for old location (deprecated)
            old_var_file = current / "variables.promptrek.yaml"
            new_var_file = current / self.LOCAL_VARIABLES_FILE

            # Handle migration from old location
            if old_var_file.exists() and not new_var_file.exists():
                self._migrate_variables_file(old_var_file, new_var_file)

            # Load from new location
            if new_var_file.exists():
                try:
                    with open(new_var_file, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if isinstance(data, dict):
                            # Extract only static variables (for backward compatibility)
                            static_vars = {}
                            for key, value in data.items():
                                if self._is_static_variable_value(value):
                                    static_vars[key] = str(value)
                            return static_vars
                        return {}
                except (OSError, UnicodeDecodeError, yaml.YAMLError):
                    # If file exists but can't be loaded, return empty dict
                    return {}

            # Move to parent directory
            parent = current.parent
            if parent == current:
                # Reached root directory
                break
            current = parent

        return {}

    def load_and_evaluate_variables(
        self,
        search_dir: Optional[Path] = None,
        allow_commands: bool = False,
        include_builtins: bool = True,
        verbose: bool = False,
        clear_cache: bool = False,
    ) -> Dict[str, str]:
        """
        Load and evaluate all variables (static, dynamic, and built-in).

        Args:
            search_dir: Directory to start search from (defaults to current dir)
            allow_commands: Whether to allow command execution for dynamic variables
            include_builtins: Whether to include built-in dynamic variables
            verbose: Whether to show verbose output
            clear_cache: Whether to clear cached dynamic variables before evaluation

        Returns:
            Dictionary of all evaluated variables

        Notes:
            Evaluation failures for dynamic variables are always printed to stdout,
            regardless of the verbose parameter.
        """
        variables = {}

        # 1. Load built-in variables (if enabled)
        if include_builtins:
            if verbose:
                print("📅 Loading built-in dynamic variables...")
            builtin_vars = BuiltInVariables.get_all(verbose=verbose)
            variables.update(builtin_vars)
            if verbose:
                print(f"  ✅ Loaded {len(builtin_vars)} built-in variable(s)")

        # 2. Load variables from file
        start_dir = search_dir if search_dir else Path.cwd()
        current = start_dir.resolve()

        var_file = None
        while True:
            # Check for old location (deprecated)
            old_var_file = current / "variables.promptrek.yaml"
            new_var_file = current / self.LOCAL_VARIABLES_FILE

            # Handle migration from old location
            if old_var_file.exists() and not new_var_file.exists():
                self._migrate_variables_file(old_var_file, new_var_file)

            # Check if file exists
            if new_var_file.exists():
                var_file = new_var_file
                break

            # Move to parent directory
            parent = current.parent
            if parent == current:
                # Reached root directory
                break
            current = parent

        if var_file is None:
            return variables

        # 3. Parse variable file
        try:
            with open(var_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                return variables

            if verbose:
                print(f"📋 Loading variables from {var_file}...")

            # Create command executor if needed
            executor = CommandExecutor(
                allow_commands=allow_commands, timeout=5, verbose=verbose
            )

            # 4. Process each variable
            static_count = 0
            dynamic_count = 0

            for key, value in data.items():
                # Static variable (string value, number, bool, or YAML date)
                if self._is_static_variable_value(value):
                    variables[key] = str(value)
                    static_count += 1

                # Dynamic variable (dict with type: command)
                elif isinstance(value, dict) and value.get("type") == "command":
                    command = value.get("value", "")
                    cache = value.get("cache", False)

                    dynamic_var = DynamicVariable(
                        name=key, command=command, cache=cache
                    )

                    if clear_cache:
                        dynamic_var.clear_cache()

                    try:
                        evaluated_value = dynamic_var.evaluate(executor)
                        variables[key] = evaluated_value
                        dynamic_count += 1
                    except TemplateError as e:
                        # Always report evaluation failures (not just in verbose mode)
                        print(f"  ⚠️  Failed to evaluate dynamic variable '{key}': {e}")
                        # Continue with other variables

            if verbose:
                print(
                    f"  ✅ Loaded {static_count} static and {dynamic_count} dynamic variable(s)"
                )

        except (OSError, UnicodeDecodeError, yaml.YAMLError) as e:
            if verbose:
                print(f"  ⚠️  Failed to load variables from {var_file}: {e}")

        return variables

    def _is_static_variable_value(self, value: Any) -> bool:
        """
        Determine if a value is considered a static variable value.

        Static variables include str, int, float, bool, and YAML date/datetime objects.

        Args:
            value: The value to check

        Returns:
            True if value is static, False otherwise
        """
        if isinstance(value, (str, int, float, bool)):
            return True
        # Handle YAML date/datetime objects precisely
        if isinstance(value, (datetime, date)):
            return True
        return False

    def _migrate_variables_file(self, old_path: Path, new_path: Path) -> None:
        """
        Migrate variables.promptrek.yaml from old location to new location.

        Args:
            old_path: Old file location (variables.promptrek.yaml in root)
            new_path: New file location (.promptrek/variables.promptrek.yaml)
        """
        import shutil

        try:
            # Only show interactive prompt if running in an interactive terminal
            if sys.stdout.isatty():
                print(
                    f"\n⚠️  DEPRECATION: Found variables file at old location: {old_path.name}"
                )
                print(f"   New location: {new_path}")
                print(
                    "   The old location is deprecated and will be removed in a future version."
                )
                response = (
                    input("\n   Migrate file to new location? [Y/n]: ").strip().lower()
                )

                if response in ("", "y", "yes"):
                    # Create .promptrek directory if it doesn't exist
                    new_path.parent.mkdir(parents=True, exist_ok=True)

                    # Move the file
                    shutil.move(str(old_path), str(new_path))
                    print(f"   ✅ Migrated {old_path.name} to {new_path}")
                    print(
                        "   💡 The file has been moved and is already gitignored via .promptrek/"
                    )
                else:
                    print(
                        "   ⏭️  Skipped migration. File will be loaded from old location."
                    )
            else:
                # Non-interactive: auto-migrate silently
                new_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(old_path), str(new_path))

        except (OSError, PermissionError, shutil.Error):
            # If migration fails due to file system errors, silently continue
            # File will be loaded from old location
            pass
