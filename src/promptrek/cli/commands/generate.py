"""
Generate command implementation.

Handles generation of editor-specific prompts from universal prompt files.
"""

import inspect
from pathlib import Path
from typing import Optional, Union

import click

from ...adapters import registry
from ...adapters.registry import AdapterCapability
from ...core.exceptions import AdapterNotFoundError, CLIError, UPFParsingError
from ...core.models import UniversalPrompt, UniversalPromptV2
from ...core.parser import UPFParser
from ...core.validator import UPFValidator
from ...utils.variables import VariableSubstitution


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

    # Load local variables from variables.promptrek.yaml
    var_sub = VariableSubstitution()
    local_vars = var_sub.load_local_variables()

    # Merge variables with precedence: CLI > local file > prompt file
    # Start with local variables, then merge CLI overrides
    merged_variables = local_vars.copy()
    if variables:
        merged_variables.update(variables)

    if verbose and local_vars:
        click.echo(f"📋 Loaded {len(local_vars)} variable(s) from local variables file")

    # Collect all files to process
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

    # Set default output directory
    if not output:
        output = Path.cwd()

    # Ensure output directory exists
    output.mkdir(parents=True, exist_ok=True)

    if dry_run:
        click.echo("🔍 Dry run mode - showing what would be generated:")

    # Process each file and collect prompts by editor
    prompts_by_editor: dict[
        str, list[tuple[Union[UniversalPrompt, UniversalPromptV2], Path]]
    ] = {}  # editor -> list of (prompt, source_file) tuples
    processing_errors = []

    for file_path in unique_files:
        try:
            file_prompts = _parse_and_validate_file(ctx, file_path)

            # Determine target editors for this file
            # V2 doesn't have targets field - works with any editor
            if isinstance(file_prompts, UniversalPromptV2):
                # V2: No targets, works with any editor
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
                merged_variables,
                headless,
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


def _parse_and_validate_file(
    ctx: click.Context, file_path: Path
) -> Union[UniversalPrompt, UniversalPromptV2]:
    """Parse and validate a single UPF file.

    Returns:
        Union[UniversalPrompt, UniversalPromptV2]: Parsed prompt (v1 or v2)
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
    prompt_files: list[tuple[Union[UniversalPrompt, UniversalPromptV2], Path]],
    editor: str,
    output_dir: Path,
    dry_run: bool,
    verbose: bool,
    variables: Optional[dict] = None,
    headless: bool = False,
) -> None:
    """Generate prompts for a specific editor from multiple UPF files."""

    try:
        adapter = registry.get(editor)

        if len(prompt_files) == 1:
            # Single file - use existing logic
            prompt, source_file = prompt_files[0]
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
            if verbose:
                click.echo(f"✅ Generated {editor} files from {source_file}")
        else:
            # Multiple files - check adapter capabilities
            if hasattr(adapter, "generate_multiple") and registry.has_capability(
                editor, AdapterCapability.MULTIPLE_FILE_GENERATION
            ):
                # Adapter supports generating separate files for each prompt
                adapter.generate_multiple(
                    prompt_files, output_dir, dry_run, verbose, variables
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
                            variables,
                            headless=headless,
                        )
                    else:
                        if headless:
                            click.echo(
                                f"Warning: {editor} adapter does not support headless mode in merged generation, ignoring --headless flag"
                            )
                        adapter.generate_merged(
                            prompt_files, output_dir, dry_run, verbose, variables
                        )
                    if verbose:
                        source_files = [str(pf[1]) for pf in prompt_files]
                        click.echo(
                            f"✅ Generated merged {editor} files from: {', '.join(source_files)}"
                        )
                except NotImplementedError:
                    # Adapter doesn't actually support merging - fall back to single file generation
                    prompt, source_file = prompt_files[-1]
                    # Check if adapter supports headless parameter
                    if _adapter_supports_headless(adapter, "generate"):
                        adapter.generate(
                            prompt,
                            output_dir,
                            dry_run,
                            verbose,
                            variables,
                            headless=headless,
                        )
                    else:
                        if headless:
                            click.echo(
                                f"Warning: {editor} adapter does not support headless mode, ignoring --headless flag"
                            )
                        adapter.generate(
                            prompt, output_dir, dry_run, verbose, variables
                        )
                    source_files = [str(pf[1]) for pf in prompt_files]
                    click.echo(
                        f"⚠️ {editor} adapter doesn't support merging. Generated from {source_file}, other files ignored: {', '.join(source_files[:-1])}"
                    )
            else:
                # Fallback: generate from last file with warning
                prompt, source_file = prompt_files[-1]
                # Check if adapter supports headless parameter
                if _adapter_supports_headless(adapter, "generate"):
                    adapter.generate(
                        prompt,
                        output_dir,
                        dry_run,
                        verbose,
                        variables,
                        headless=headless,
                    )
                else:
                    if headless:
                        click.echo(
                            f"Warning: {editor} adapter does not support headless mode, ignoring --headless flag"
                        )
                    adapter.generate(prompt, output_dir, dry_run, verbose, variables)
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
    prompt: Union[UniversalPrompt, UniversalPromptV2],
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
