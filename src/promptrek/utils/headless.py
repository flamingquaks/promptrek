"""Bootstrap file generation for headless/managed agents.

This module provides utilities for generating bootstrap files that enable
AI agents to automatically regenerate PrompTrek configurations in headless
environments (CI/CD, remote servers, managed agents without local IDE).
"""

from typing import Optional


def generate_bootstrap_content(
    editor_name: str,
    editor_display_name: str,
    generated_file_paths: list[str],
    custom_message: Optional[str] = None,
    promptrek_version: str = "0.6.0",
) -> str:
    """Generate bootstrap file content with YAML frontmatter and markdown.

    Args:
        editor_name: Internal editor name (e.g., "claude", "copilot")
        editor_display_name: Human-readable editor name (e.g., "Claude", "GitHub Copilot")
        generated_file_paths: List of file paths that will be generated
        custom_message: Optional custom message from project config
        promptrek_version: PrompTrek version string

    Returns:
        Complete bootstrap file content with YAML frontmatter and markdown
    """
    # YAML frontmatter for machine parsing
    yaml_frontmatter = f"""---
promptrek_bootstrap: true
auto_execute: true
version: "1.0.0"
editor: "{editor_name}"

pre_flight_checks:
  - name: "Check PrompTrek CLI"
    check_command: "promptrek"
    error_message: "PrompTrek CLI not found. Install with: pip install promptrek"

  - name: "Validate Configuration"
    command: "promptrek validate project.promptrek.yaml"
    error_message: "Configuration validation failed. Check project.promptrek.yaml"

steps:
  - name: "Generate {editor_display_name} Configurations"
    command: "promptrek generate --editor {editor_name} --headless"
    description: "Regenerates {editor_display_name} config files with latest variables"
    required: true

  - name: "Verify Generation"
    check_files_exist: {generated_file_paths}
    error_message: "Configuration files were not generated successfully"

post_bootstrap:
  message: "✅ PrompTrek bootstrap complete for {editor_display_name}"
  next_action: "follow_generated_instructions"
  instructions: "Follow the instructions in your generated {editor_display_name} configuration files"
---
"""

    # Markdown content for humans and agent context
    markdown_content = f"""# PrompTrek Bootstrap Instructions for {editor_display_name}

**🤖 AUTOMATED BOOTSTRAP DETECTED**

This file indicates that full configuration files need to be generated from
the project's `project.promptrek.yaml` source of truth.

## What is PrompTrek?

PrompTrek is a universal AI editor prompt management tool that converts a
single `project.promptrek.yaml` configuration into editor-specific files
for various AI coding assistants (GitHub Copilot, Cursor, Continue, Claude Code,
Windsurf, Cline, Kiro, Amazon Q, JetBrains AI, Tabnine).

**Key Benefits:**
- 📝 Single source of truth for all editor configurations
- 🔄 Bidirectional sync between YAML and editor files
- 🎯 No merge conflicts on generated files
- 🔧 Variable substitution and dynamic content
- 🤝 Team-wide consistency

## Why Run Generation?

The full instructions are **not committed to git** because PrompTrek maintains
the source of truth in `project.promptrek.yaml`. This ensures:

- **DRY Principle**: Write configuration once, generate for all editors
- **No Merge Conflicts**: Generated files are gitignored, only source is versioned
- **Easy Synchronization**: Team members run `promptrek generate` to get latest config
- **Variable Substitution**: Environment-specific values injected at generation time

## For AI Agents: Automatic Execution

**If you're an AI agent reading this**, you should automatically execute the following:

### Pre-flight Checks
1. Verify PrompTrek CLI is installed: `which promptrek || pip install promptrek`
2. Validate configuration: `promptrek validate project.promptrek.yaml`

### Generate Configurations
```bash
promptrek generate --editor {editor_name} --headless
```

This command will regenerate the full configuration files you need to assist with this project.

### Expected Output Files
After generation, these files will be available:
"""

    # Add generated file paths
    for path in generated_file_paths:
        markdown_content += f"\n- `{path}`"

    # Add custom message if provided
    if custom_message:
        markdown_content += f"""

## Project-Specific Instructions

{custom_message}
"""

    # Add manual instructions for humans
    markdown_content += f"""

## For Humans: Manual Execution

If PrompTrek is not installed, install it first:

```bash
# Using pip
pip install promptrek

# Using uv (recommended)
uv pip install promptrek

# Using pipx (isolated installation)
pipx install promptrek
```

Then generate configurations for {editor_display_name}:

```bash
# Generate for {editor_display_name} only
promptrek generate --editor {editor_name}

# Or generate for all configured editors
promptrek generate --all

# Interactive mode
promptrek
```

## Next Steps

After generation completes:

1. ✅ Full configuration files will be available in their respective locations
2. 📖 Follow the instructions in the generated files
3. 🚀 Start working with the latest project context and guidelines

## Troubleshooting

**Configuration validation fails:**
- Check `project.promptrek.yaml` for syntax errors
- Run `promptrek validate project.promptrek.yaml` for detailed error messages

**Generation fails:**
- Ensure you're in the project root directory (where `project.promptrek.yaml` exists)
- Check file permissions for write access to generated file locations
- Verify PrompTrek version is up to date: `promptrek --version`

**Generated files not appearing:**
- Check the expected file paths listed above
- Some editors use different locations based on your setup
- Run with verbose output: `promptrek generate --editor {editor_name} --verbose`

## Learn More

- 📚 Documentation: https://github.com/promptrek/promptrek
- 🐛 Report Issues: https://github.com/promptrek/promptrek/issues
- 💬 Discussions: https://github.com/promptrek/promptrek/discussions

---

*This bootstrap file was generated by PrompTrek v{promptrek_version}*
*Source: `project.promptrek.yaml`*
*Editor: {editor_display_name} ({editor_name})*
"""

    return yaml_frontmatter + markdown_content


def generate_inline_bootstrap_marker(
    editor_name: str,
    editor_display_name: str,
    comment_style: str = "html",
) -> str:
    """Generate inline bootstrap marker for embedding in existing files.

    Some editors (like Copilot) embed bootstrap instructions directly in
    the generated file rather than creating a separate bootstrap file.

    Args:
        editor_name: Internal editor name
        editor_display_name: Human-readable editor name
        comment_style: Comment syntax ("html", "hash", "yaml")

    Returns:
        Inline bootstrap marker text
    """
    if comment_style == "html":
        return f"""<!-- PROMPTREK HEADLESS BOOTSTRAP START -->
<!--
🤖 HEADLESS AGENT INSTRUCTIONS:

Before starting any coding tasks, regenerate the latest configuration:

    promptrek generate --editor {editor_name} --headless

This ensures you have the most up-to-date project context, guidelines,
and editor-specific instructions from project.promptrek.yaml.

Why? The full configuration is generated from a single source of truth
and should not be edited directly. PrompTrek maintains consistency across
all AI coding assistants and team members.

For more information: https://github.com/promptrek/promptrek
-->
<!-- PROMPTREK HEADLESS BOOTSTRAP END -->
"""
    elif comment_style == "hash":
        return f"""# PROMPTREK HEADLESS BOOTSTRAP START
#
# 🤖 HEADLESS AGENT INSTRUCTIONS:
#
# Before starting any coding tasks, regenerate the latest configuration:
#
#     promptrek generate --editor {editor_name} --headless
#
# This ensures you have the most up-to-date project context, guidelines,
# and editor-specific instructions from project.promptrek.yaml.
#
# Why? The full configuration is generated from a single source of truth
# and should not be edited directly. PrompTrek maintains consistency across
# all AI coding assistants and team members.
#
# For more information: https://github.com/promptrek/promptrek
#
# PROMPTREK HEADLESS BOOTSTRAP END
"""
    elif comment_style == "yaml":
        return f"""# PROMPTREK HEADLESS BOOTSTRAP START
# Auto-execute: promptrek generate --editor {editor_name} --headless
# Editor: {editor_display_name}
# Documentation: https://github.com/promptrek/promptrek
# PROMPTREK HEADLESS BOOTSTRAP END
"""
    else:
        raise ValueError(f"Unknown comment style: {comment_style}")
