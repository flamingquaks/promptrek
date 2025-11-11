"""
Generate command implementation.

Handles generation of editor-specific prompts from universal prompt files.
"""

import inspect
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import click
import yaml

from ...adapters import registry
from ...adapters.registry import AdapterCapability
from ...commands.spec_commands import get_spec_commands
from ...core.exceptions import AdapterNotFoundError, CLIError, UPFParsingError
from ...core.models import (
    DynamicVariableConfig,
    GenerationMetadata,
    UniversalPrompt,
    UniversalPromptV2,
    UniversalPromptV3,
)
from ...core.parser import UPFParser
from ...core.validator import UPFValidator
from ...utils.spec_manager import SpecManager
from ...utils.variables import BuiltInVariables, VariableSubstitution


def _adapter_supports_headless(adapter: object, method_name: str) -> bool:
    """
    Check if an adapter method supports the 'headless' parameter.

    Uses inspect.signature() for reliable parameter detection.

    Args:
        adapter: The adapter instance
        method_name: Name of the method to check ('generate' or 'generate_merged')

    Returns:
        bool: True if the method supports headless parameter
    """
    try:
        if not hasattr(adapter, method_name):
            return False

        method = getattr(adapter, method_name)
        sig = inspect.signature(method)
        return "headless" in sig.parameters
    except (ValueError, TypeError):
        # Fallback to False if signature inspection fails
        return False


def generate_command(
    ctx: click.Context,
    files: tuple[Path, ...],
    directory: Optional[Path],
    recursive: bool,
    editor: Optional[str],
    output: Optional[Path],
    dry_run: bool,
    all_editors: bool,
    variables: Optional[dict] = None,
    headless: bool = False,
) -> None:
    """
    Generate editor-specific prompts from universal prompt files.

    Args:
        ctx: Click context
        files: Tuple of file paths to process
        directory: Directory to search for UPF files
        recursive: Whether to search recursively in directories
        editor: Target editor name
        output: Output directory path
        dry_run: Whether to show what would be generated without creating files
        all_editors: Whether to generate for all target editors
        variables: Variable overrides
    """
    verbose = ctx.obj.get("verbose", False)

    # Collect all files to process first (we need to check allow_commands from prompts)
    files_to_process: list[Path] = []

    # Add explicitly specified files
    files_to_process.extend(list(files))

    # Add files from directory if specified
    if directory:
        parser = UPFParser()
        found_files = parser.find_upf_files(directory, recursive)
        files_to_process.extend(found_files)
        if verbose:
            click.echo(f"Found {len(found_files)} UPF files in {directory}")

    # If no files specified and no directory, look in current directory
    if not files_to_process and not directory:
        parser = UPFParser()
        found_files = parser.find_upf_files(Path.cwd(), recursive=False)
        if found_files:
            files_to_process.extend(found_files)
            if verbose:
                click.echo(f"Found {len(found_files)} UPF files in current directory")

    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for file_path in files_to_process:
        if file_path not in seen:
            seen.add(file_path)
            unique_files.append(file_path)

    if not unique_files:
        raise CLIError(
            "No UPF files found. Specify files directly or use --directory option."
        )

    if verbose:
        click.echo(f"Processing {len(unique_files)} file(s):")
        for file_path in unique_files:
            click.echo(f"  - {file_path}")

    # Determine allow_commands setting by checking first file
    # This is needed before loading variables to know if command execution is allowed
    allow_commands = False
    try:
        first_prompt = _parse_and_validate_file(ctx, unique_files[0])
        if isinstance(first_prompt, UniversalPromptV3):
            allow_commands = first_prompt.allow_commands or False
    except (UPFParsingError, CLIError):
        # If parsing fails, it will be caught again in the main loop
        pass
    except Exception as exc:
        if verbose:
            click.echo(
                f"Unexpected error while parsing {unique_files[0]}: {exc}", err=True
            )

    # Load and evaluate variables (including built-in and dynamic variables)
    # These are: built-in + local file variables (without CLI overrides yet)
    var_sub = VariableSubstitution()
    base_variables = var_sub.load_and_evaluate_variables(
        allow_commands=allow_commands,
        include_builtins=True,
        verbose=verbose,
        clear_cache=False,
    )

    # Keep CLI overrides separate for now to ensure correct precedence
    # Precedence: built-in < local < prompt.variables < CLI
    cli_overrides = variables or {}

    if verbose and base_variables:
        click.echo(
            f"✅ Loaded {len(base_variables)} base variable(s) (built-in + local)"
        )

    # Set default output directory
    if not output:
        output = Path.cwd()

    # Ensure output directory exists
    output.mkdir(parents=True, exist_ok=True)

    if dry_run:
        click.echo("🔍 Dry run mode - showing what would be generated:")

    # Process each file and collect prompts by editor
    prompts_by_editor: dict[
        str,
        list[tuple[Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3], Path]],
    ] = {}  # editor -> list of (prompt, source_file) tuples
    processing_errors = []

    for file_path in unique_files:
        try:
            file_prompts = _parse_and_validate_file(ctx, file_path)

            # Determine target editors for this file
            # V2/V3 doesn't have targets field - works with any editor
            if isinstance(file_prompts, (UniversalPromptV2, UniversalPromptV3)):
                # V2/V3: No targets, works with any editor
                if all_editors:
                    target_editors = registry.get_project_file_adapters()
                elif editor:
                    target_editors = [editor]
                else:
                    raise CLIError("Must specify either --editor or --all")
            else:
                # V1: Has targets field
                file_targets = file_prompts.targets or []
                if all_editors:
                    target_editors = file_targets
                elif editor:
                    # If targets is None (not specified), allow any editor
                    if (
                        file_prompts.targets is not None
                        and editor not in file_prompts.targets
                    ):
                        # For single file scenario, this should be an error for backward compatibility
                        if len(unique_files) == 1:
                            raise CLIError(
                                f"Editor '{editor}' not in targets for {file_path}: {', '.join(file_targets)}"
                            )
                        # For multiple files, just skip with a warning
                        if verbose:
                            click.echo(
                                f"⚠️ Editor '{editor}' not in targets for {file_path}, skipping"
                            )
                        continue
                    target_editors = [editor]
                else:
                    # This is a critical error that should stop processing
                    raise CLIError("Must specify either --editor or --all")

            # Add to prompts by editor
            for target_editor in target_editors:
                if target_editor not in prompts_by_editor:
                    prompts_by_editor[target_editor] = []
                prompts_by_editor[target_editor].append((file_prompts, file_path))

        except CLIError:
            # Re-raise CLIError immediately (these are critical errors)
            raise
        except Exception as e:
            processing_errors.append((file_path, str(e)))
            if verbose:
                click.echo(f"❌ Error processing {file_path}: {e}", err=True)
                # Continue processing other files for non-critical errors
                continue
            else:
                click.echo(f"❌ Error processing {file_path}: {e}", err=True)
                continue

    # Check if we had processing errors but no successful files
    if processing_errors and not prompts_by_editor:
        # All files failed, report the first error
        first_error_file, first_error_msg = processing_errors[0]
        raise CLIError(f"Failed to process {first_error_file}: {first_error_msg}")

    # Generate for each editor with all collected prompts
    generation_errors = []
    for target_editor, prompt_files in prompts_by_editor.items():
        try:
            _generate_for_editor_multiple(
                prompt_files,
                target_editor,
                output,
                dry_run,
                verbose,
                variables=None,  # Deprecated param
                headless=headless,
                base_variables=base_variables,
                cli_overrides=cli_overrides,
            )
        except AdapterNotFoundError:
            click.echo(f"⚠️ Editor '{target_editor}' not yet implemented - skipping")
        except Exception as e:
            generation_errors.append((target_editor, str(e)))
            if verbose:
                raise
            click.echo(f"❌ Failed to generate for {target_editor}: {e}", err=True)
            # Continue with other editors

    # If we had generation errors but no successful generations, report error
    if generation_errors and not any(prompts_by_editor.values()):
        first_error_editor, first_error_msg = generation_errors[0]
        raise CLIError(
            f"Failed to generate for {first_error_editor}: {first_error_msg}"
        )

    # Save generation metadata for refresh command (skip in dry-run mode)
    if not dry_run and prompts_by_editor:
        try:
            # Merge base + CLI for metadata (not including prompt.variables)
            metadata_vars = {}
            if base_variables:
                metadata_vars.update(base_variables)
            if cli_overrides:
                metadata_vars.update(cli_overrides)

            _save_generation_metadata(
                source_files=unique_files,
                editors=list(prompts_by_editor.keys()),
                output_dir=output,
                variables=metadata_vars,
                allow_commands=allow_commands,
                verbose=verbose,
            )
        except Exception as e:
            if verbose:
                click.echo(f"⚠️ Failed to save generation metadata: {e}", err=True)
            # Don't fail the whole generation if metadata saving fails


def _save_generation_metadata(
    source_files: list[Path],
    editors: list[str],
    output_dir: Path,
    variables: dict[str, str],
    allow_commands: bool,
    verbose: bool = False,
) -> None:
    """Save generation metadata for refresh command."""
    # Create .promptrek directory if it doesn't exist
    promptrek_dir = Path.cwd() / ".promptrek"
    promptrek_dir.mkdir(parents=True, exist_ok=True)

    metadata_file = promptrek_dir / "last-generation.yaml"

    # Load current variables file to extract dynamic variable configs
    var_sub = VariableSubstitution()
    dynamic_vars = {}

    var_file = None
    current = Path.cwd().resolve()
    while True:
        test_file = current / ".promptrek/variables.promptrek.yaml"
        if test_file.exists():
            var_file = test_file
            break
        parent = current.parent
        if parent == current:
            break
        current = parent

    if var_file:
        try:
            with open(var_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, dict) and value.get("type") == "command":
                            dynamic_vars[key] = DynamicVariableConfig(
                                type="command",
                                value=value.get("value", ""),
                                cache=value.get("cache", False),
                            )
        except Exception:
            pass  # Ignore errors loading variable file

    # Extract only static variables (exclude dynamic and built-in)
    static_vars = {}
    # Get built-in variable names dynamically from BuiltInVariables (once)
    builtin_var_names = set(BuiltInVariables.get_all().keys())

    for key, value in variables.items():
        if key not in builtin_var_names and key not in dynamic_vars:
            static_vars[key] = value

    # Create metadata
    metadata = GenerationMetadata(
        timestamp=datetime.now().isoformat(),
        source_file=str(source_files[0]) if source_files else "",
        editors=editors,
        output_dir=str(output_dir),
        variables=static_vars,
        dynamic_variables=dynamic_vars,
        builtin_variables_enabled=True,
        allow_commands=allow_commands,
    )

    # Save to file
    try:
        with open(metadata_file, "w", encoding="utf-8") as f:
            yaml.dump(
                metadata.model_dump(by_alias=True),
                f,
                default_flow_style=False,
                sort_keys=False,
            )

        if verbose:
            click.echo(f"💾 Saved generation metadata to {metadata_file}")
    except (OSError, PermissionError) as e:
        click.echo(
            f"⚠️  Warning: Failed to save generation metadata to {metadata_file}: {e}",
            err=True,
        )
        if verbose:
            click.echo(
                "   Metadata is used for tracking generation history. "
                "Generation will continue without it.",
                err=True,
            )


def _inject_spec_commands(
    prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
    output_dir: Path,
) -> Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]:
    """
    Inject spec-driven project document commands into the prompt.

    This ensures the spec management commands are available in all editors.

    Args:
        prompt: The prompt to inject commands into
        output_dir: Output directory (used to determine project root)

    Returns:
        Modified prompt with spec commands injected
    """
    # Only inject for V2 and V3 prompts (they support commands)
    if not isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
        return prompt

    # Initialize spec manager to ensure directory exists
    spec_manager = SpecManager(output_dir)
    spec_manager.ensure_specs_directory()

    # Only inject spec commands for v3.1.0+ (spec support is a v3.1+ feature)
    should_inject_specs = False
    if isinstance(prompt, UniversalPromptV3):
        # Parse schema version (format: "major.minor.patch")
        try:
            version_parts = prompt.schema_version.split(".")
            major = int(version_parts[0])
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0

            # Require v3.1.0 or greater
            if major >= 3 and minor >= 1:
                should_inject_specs = True
        except (ValueError, IndexError):
            # Invalid version format, default to not injecting
            pass

    # Inject spec commands if version check passed
    if should_inject_specs:
        # Get spec commands
        spec_commands = get_spec_commands()

        # For V3.1+, inject into top-level commands field
        if isinstance(prompt, UniversalPromptV3):
            if prompt.commands is None:
                prompt.commands = []
            # Only add commands that don't already exist
            existing_names = {cmd.name for cmd in prompt.commands}
            for spec_cmd in spec_commands:
                if spec_cmd.name not in existing_names:
                    prompt.commands.append(spec_cmd)

    return prompt


def _parse_and_validate_file(
    ctx: click.Context, file_path: Path
) -> Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]:
    """Parse and validate a single UPF file.

    Returns:
        Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]: Parsed prompt (v1, v2, or v3)
    """
    verbose = ctx.obj.get("verbose", False)

    # Parse the file
    parser = UPFParser()
    try:
        prompt = parser.parse_file(file_path)
        if verbose:
            click.echo(f"✅ Parsed {file_path}")
    except UPFParsingError as e:
        raise CLIError(f"Failed to parse {file_path}: {e}")

    # Validate first
    validator = UPFValidator()
    result = validator.validate(prompt)
    if result.errors:
        raise CLIError(f"Validation failed for {file_path}: {'; '.join(result.errors)}")

    return prompt


def _generate_for_editor_multiple(
    prompt_files: list[
        tuple[Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3], Path]
    ],
    editor: str,
    output_dir: Path,
    dry_run: bool,
    verbose: bool,
    variables: Optional[dict] = None,
    headless: bool = False,
    base_variables: Optional[dict] = None,
    cli_overrides: Optional[dict] = None,
) -> None:
    """Generate prompts for a specific editor from multiple UPF files.

    Args:
        prompt_files: List of (prompt, source_file) tuples
        editor: Target editor name
        output_dir: Output directory
        dry_run: Dry run mode
        verbose: Verbose output
        variables: DEPRECATED - use base_variables and cli_overrides instead
        headless: Headless mode
        base_variables: Built-in + local file variables
        cli_overrides: CLI variable overrides (-V options)
    """

    try:
        adapter = registry.get(editor)

        if len(prompt_files) == 1:
            # Single file - merge variables with correct precedence
            prompt, source_file = prompt_files[0]

            # Inject spec commands into prompt
            prompt = _inject_spec_commands(prompt, output_dir)

            # Merge variables: base < prompt.variables < CLI < EDITOR_NAME (auto-injected)
            merged_vars = {}
            if base_variables:
                merged_vars.update(base_variables)
            if hasattr(prompt, "variables") and prompt.variables:
                merged_vars.update(prompt.variables)
            if cli_overrides:
                merged_vars.update(cli_overrides)
            # Fallback to old 'variables' param for backward compatibility
            if variables and not (base_variables or cli_overrides):
                merged_vars = variables

            # Auto-inject EDITOR_NAME for dynamic editor references
            merged_vars["EDITOR_NAME"] = editor

            # Check if adapter supports headless parameter
            if _adapter_supports_headless(adapter, "generate"):
                adapter.generate(
                    prompt, output_dir, dry_run, verbose, merged_vars, headless=headless
                )
            else:
                if headless:
                    click.echo(
                        f"Warning: {editor} adapter does not support headless mode, ignoring --headless flag"
                    )
                adapter.generate(prompt, output_dir, dry_run, verbose, merged_vars)
            if verbose:
                click.echo(f"✅ Generated {editor} files from {source_file}")
        else:
            # Multiple files - inject spec commands into all prompts
            prompt_files = [
                (_inject_spec_commands(prompt, output_dir), source_file)
                for prompt, source_file in prompt_files
            ]

            # For merged generation, we'll use the last prompt's variables
            # TODO: In future, support merging variables from multiple prompts
            last_prompt = prompt_files[-1][0]
            merged_vars = {}
            if base_variables:
                merged_vars.update(base_variables)
            if hasattr(last_prompt, "variables") and last_prompt.variables:
                merged_vars.update(last_prompt.variables)
            if cli_overrides:
                merged_vars.update(cli_overrides)
            if variables and not (base_variables or cli_overrides):
                merged_vars = variables

            # Auto-inject EDITOR_NAME for dynamic editor references
            merged_vars["EDITOR_NAME"] = editor

            # Multiple files - check adapter capabilities
            if hasattr(adapter, "generate_multiple") and registry.has_capability(
                editor, AdapterCapability.MULTIPLE_FILE_GENERATION
            ):
                # Adapter supports generating separate files for each prompt
                adapter.generate_multiple(
                    prompt_files, output_dir, dry_run, verbose, merged_vars
                )
                click.echo(f"Generated separate {editor} files")
            elif hasattr(adapter, "generate_merged"):
                # Other adapters use merged files - try to use generate_merged
                try:
                    # Check if adapter supports headless parameter in generate_merged
                    if _adapter_supports_headless(adapter, "generate_merged"):
                        adapter.generate_merged(
                            prompt_files,
                            output_dir,
                            dry_run,
                            verbose,
                            merged_vars,
                            headless=headless,
                        )
                    else:
                        if headless:
                            click.echo(
                                f"Warning: {editor} adapter does not support headless mode in merged generation, ignoring --headless flag"
                            )
                        adapter.generate_merged(
                            prompt_files, output_dir, dry_run, verbose, merged_vars
                        )
                    if verbose:
                        source_files = [str(pf[1]) for pf in prompt_files]
                        click.echo(
                            f"✅ Generated merged {editor} files from: {', '.join(source_files)}"
                        )
                except NotImplementedError:
                    # Adapter doesn't actually support merging - fall back to single file generation
                    prompt, source_file = prompt_files[-1]
                    # Re-merge variables for this specific prompt
                    fallback_vars = {}
                    if base_variables:
                        fallback_vars.update(base_variables)
                    if hasattr(prompt, "variables") and prompt.variables:
                        fallback_vars.update(prompt.variables)
                    if cli_overrides:
                        fallback_vars.update(cli_overrides)
                    if variables and not (base_variables or cli_overrides):
                        fallback_vars = variables

                    # Check if adapter supports headless parameter
                    if _adapter_supports_headless(adapter, "generate"):
                        adapter.generate(
                            prompt,
                            output_dir,
                            dry_run,
                            verbose,
                            fallback_vars,
                            headless=headless,
                        )
                    else:
                        if headless:
                            click.echo(
                                f"Warning: {editor} adapter does not support headless mode, ignoring --headless flag"
                            )
                        adapter.generate(
                            prompt, output_dir, dry_run, verbose, fallback_vars
                        )
                    source_files = [str(pf[1]) for pf in prompt_files]
                    click.echo(
                        f"⚠️ {editor} adapter doesn't support merging. Generated from {source_file}, other files ignored: {', '.join(source_files[:-1])}"
                    )
            else:
                # Fallback: generate from last file with warning
                prompt, source_file = prompt_files[-1]
                fallback_vars = {}
                if base_variables:
                    fallback_vars.update(base_variables)
                if hasattr(prompt, "variables") and prompt.variables:
                    fallback_vars.update(prompt.variables)
                if cli_overrides:
                    fallback_vars.update(cli_overrides)
                if variables and not (base_variables or cli_overrides):
                    fallback_vars = variables

                # Check if adapter supports headless parameter
                if _adapter_supports_headless(adapter, "generate"):
                    adapter.generate(
                        prompt,
                        output_dir,
                        dry_run,
                        verbose,
                        fallback_vars,
                        headless=headless,
                    )
                else:
                    if headless:
                        click.echo(
                            f"Warning: {editor} adapter does not support headless mode, ignoring --headless flag"
                        )
                    adapter.generate(
                        prompt, output_dir, dry_run, verbose, fallback_vars
                    )
                source_files = [str(pf[1]) for pf in prompt_files]
                click.echo(
                    f"⚠️ {editor} adapter doesn't support merging. Generated from {source_file}, other files ignored: {', '.join(source_files[:-1])}"
                )

    except AdapterNotFoundError:
        raise AdapterNotFoundError(f"Editor '{editor}' adapter not implemented yet")


def _process_single_file(
    ctx: click.Context,
    file_path: Path,
    editor: Optional[str],
    output: Path,
    dry_run: bool,
    all_editors: bool,
    variables: Optional[dict] = None,
    headless: bool = False,
) -> None:
    """Process a single UPF file."""
    verbose = ctx.obj.get("verbose", False)

    prompt = _parse_and_validate_file(ctx, file_path)

    # Determine target editors
    if all_editors:
        # Get all adapters but separate by capability
        project_file_adapters = registry.get_project_file_adapters()
        global_config_adapters = registry.get_global_config_adapters()
        ide_plugin_adapters = registry.get_adapters_by_capability(
            AdapterCapability.IDE_PLUGIN_ONLY
        )

        target_editors = project_file_adapters

        # Show information about non-project-file tools
        if global_config_adapters or ide_plugin_adapters:
            click.echo("ℹ️  Note: Some tools use global configuration only:")
            for adapter_name in global_config_adapters:
                click.echo(f"  - {adapter_name}: Configure through global settings")
            for adapter_name in ide_plugin_adapters:
                click.echo(f"  - {adapter_name}: Configure through IDE interface")
            click.echo()
    elif editor:
        # Check if the adapter exists and what capabilities it has
        available_adapters = registry.list_adapters()
        if editor not in available_adapters:
            raise CLIError(
                f"Editor '{editor}' not available. Available editors: {', '.join(available_adapters)}"
            )

        # Check if this adapter supports project files
        if not registry.has_capability(
            editor, AdapterCapability.GENERATES_PROJECT_FILES
        ):
            # Provide helpful information instead of generating files
            adapter_info = registry.get_adapter_info(editor)
            capabilities = adapter_info.get("capabilities", [])

            if AdapterCapability.GLOBAL_CONFIG_ONLY.value in capabilities:
                click.echo(f"ℹ️  {editor} uses global configuration only.")
                click.echo(
                    f"   Configure {editor} through its global settings or admin panel."
                )
            elif AdapterCapability.IDE_PLUGIN_ONLY.value in capabilities:
                click.echo(f"ℹ️  {editor} is configured through IDE interface only.")
                click.echo(
                    f"   Configure {editor} through your IDE's settings or preferences."
                )
            else:
                click.echo(
                    f"ℹ️  {editor} does not support project-level configuration files."
                )

            return  # Exit early without generating files

        target_editors = [editor]
    else:
        raise CLIError("Must specify either --editor or --all")

    # Set default output directory
    if not output:
        output = Path.cwd()

    # Ensure output directory exists
    output.mkdir(parents=True, exist_ok=True)

    if dry_run:
        click.echo("🔍 Dry run mode - showing what would be generated:")

    if target_editors:
        click.echo("Generating project configuration files for:")

    # Generate for each target editor that supports project files
    for target_editor in target_editors:
        try:
            _generate_for_editor(
                prompt,
                target_editor,
                output,
                dry_run,
                verbose,
                variables,
                file_path,
                headless,
            )
        except AdapterNotFoundError:
            click.echo(f"⚠️ Editor '{target_editor}' not yet implemented - skipping")
        except Exception as e:
            if verbose:
                raise
            raise CLIError(
                f"Failed to generate for {target_editor} from {file_path}: {e}"
            )


def _generate_for_editor(
    prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
    editor: str,
    output_dir: Path,
    dry_run: bool,
    verbose: bool,
    variables: Optional[dict] = None,
    source_file: Optional[Path] = None,
    headless: bool = False,
) -> None:
    """Generate prompts for a specific editor using the adapter system."""

    try:
        adapter = registry.get(editor)
        # Check if adapter supports headless parameter
        if _adapter_supports_headless(adapter, "generate"):
            adapter.generate(
                prompt, output_dir, dry_run, verbose, variables, headless=headless
            )
        else:
            if headless:
                click.echo(
                    f"Warning: {editor} adapter does not support headless mode, ignoring --headless flag"
                )
            adapter.generate(prompt, output_dir, dry_run, verbose, variables)

        if verbose and source_file:
            click.echo(f"✅ Generated {editor} files from {source_file}")
    except AdapterNotFoundError:
        raise AdapterNotFoundError(f"Editor '{editor}' adapter not implemented yet")
