# MCP Generation Mixin

The MCP generation mixin provides shared functionality for editor adapters to generate Model Context Protocol (MCP) server configurations.

## Overview

The `MCPGenerationMixin` class provides a reusable implementation for MCP server configuration generation with:

- **Project-first strategy**: Prefers project-level MCP configuration when supported
- **System-wide fallback**: Falls back to user/system config with confirmation
- **Configuration merging**: Safely merges new MCP servers with existing configurations
- **Conflict detection**: Identifies and handles MCP servers with same name but different settings
- **User confirmation**: Prompts for approval when modifying system-wide settings
- **Format flexibility**: Supports different MCP configuration formats

Editor adapters can inherit from this mixin to get MCP generation capabilities without reimplementing the logic.

## API Reference

::: promptrek.adapters.mcp_mixin
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      docstring_style: google
      show_if_no_docstring: false

## Usage Examples

### Using the Mixin in an Adapter

Inherit from MCPGenerationMixin in your adapter:

```python
from pathlib import Path
from typing import Dict, Any, List
from promptrek.adapters.base import EditorAdapter
from promptrek.adapters.mcp_mixin import MCPGenerationMixin

class MyEditorAdapter(EditorAdapter, MCPGenerationMixin):
    """Adapter with MCP support."""

    def __init__(self):
        super().__init__(
            name="my-editor",
            description="Editor with MCP support",
            file_patterns=[".myeditor/config.json"]
        )

    def get_mcp_config_strategy(self) -> Dict[str, Any]:
        """Define MCP configuration strategy."""
        return {
            "supports_project": True,  # Supports project-level config
            "project_path": ".myeditor/mcp.json",  # Project config path
            "system_path": None,  # System path (if needed)
            "requires_confirmation": True,
            "config_format": "json"
        }

    def generate(self, prompt, output_dir, **kwargs):
        """Generate files including MCP config."""
        files = []

        # Generate MCP configuration if present
        if hasattr(prompt, 'mcp_servers') and prompt.mcp_servers:
            mcp_files = self._generate_mcp_config(
                prompt.mcp_servers,
                output_dir,
                kwargs.get('variables'),
                kwargs.get('dry_run', False),
                kwargs.get('verbose', False)
            )
            files.extend(mcp_files)

        return files

    def _generate_mcp_config(
        self,
        mcp_servers,
        output_dir,
        variables,
        dry_run,
        verbose
    ):
        """Generate MCP configuration using mixin methods."""
        strategy = self.get_mcp_config_strategy()

        if strategy["supports_project"]:
            # Project-level config
            config_path = output_dir / strategy["project_path"]

            # Build MCP config
            mcp_config = self.build_mcp_servers_config(
                mcp_servers,
                variables=variables,
                format_style="standard"
            )

            # Read existing config
            existing = self.read_existing_mcp_config(config_path)

            if existing:
                # Merge with existing
                merged = self.merge_mcp_config(existing, mcp_config)
                mcp_config = merged

            # Write config
            self.write_mcp_config_file(
                mcp_config,
                config_path,
                dry_run,
                verbose
            )

            return [config_path]

        return []
```

### Building MCP Server Configuration

Create MCP server configurations from models:

```python
from promptrek.adapters.mcp_mixin import MCPGenerationMixin
from promptrek.core.models import MCPServer

mixin = MCPGenerationMixin()

# Define MCP servers
servers = [
    MCPServer(
        name="filesystem",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/project"],
        description="Project filesystem access"
    ),
    MCPServer(
        name="github",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_TOKEN": "{{{ GITHUB_TOKEN }}}"},
        description="GitHub API access"
    )
]

# Build configuration
config = mixin.build_mcp_servers_config(
    servers,
    variables={"GITHUB_TOKEN": "ghp_xxxxx"},
    format_style="standard"
)

# Result:
# {
#     "mcpServers": {
#         "filesystem": {
#             "command": "npx",
#             "args": ["-y", "@modelcontextprotocol/server-filesystem", "/project"],
#             "description": "Project filesystem access"
#         },
#         "github": {
#             "command": "npx",
#             "args": ["-y", "@modelcontextprotocol/server-github"],
#             "env": {"GITHUB_TOKEN": "ghp_xxxxx"},
#             "description": "GitHub API access"
#         }
#     }
# }
```

### Merging MCP Configurations

Merge new MCP servers with existing configuration:

```python
from promptrek.adapters.mcp_mixin import MCPGenerationMixin

mixin = MCPGenerationMixin()

# Existing configuration
existing = {
    "mcpServers": {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/old-path"]
        },
        "old-server": {
            "command": "old-command"
        }
    },
    "other_settings": {
        "theme": "dark"
    }
}

# New MCP configuration
new_mcp = {
    "mcpServers": {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/new-path"]
        },
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"]
        }
    }
}

# Merge
merged = mixin.merge_mcp_config(existing, new_mcp, format_style="standard")

# Result:
# {
#     "mcpServers": {
#         "filesystem": {  # Updated
#             "command": "npx",
#             "args": ["-y", "@modelcontextprotocol/server-filesystem", "/new-path"]
#         },
#         "old-server": {  # Preserved
#             "command": "old-command"
#         },
#         "github": {  # Added
#             "command": "npx",
#             "args": ["-y", "@modelcontextprotocol/server-github"]
#         }
#     },
#     "other_settings": {  # Preserved
#         "theme": "dark"
#     }
# }
```

### Detecting Configuration Conflicts

Identify MCP servers with conflicting configurations:

```python
from promptrek.adapters.mcp_mixin import MCPGenerationMixin

mixin = MCPGenerationMixin()

# Existing configuration
existing = {
    "mcpServers": {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path1"]
        }
    }
}

# New servers to add
new_servers = {
    "filesystem": {  # Same name, different config
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path2"]
    },
    "github": {  # New server, no conflict
        "command": "npx"
    }
}

# Detect conflicts
conflicts = mixin.detect_conflicting_servers(new_servers, existing)
print(f"Conflicting servers: {conflicts}")
# Output: ['filesystem']

# Handle conflicts
for server_name in conflicts:
    print(f"Server '{server_name}' has different configuration")
    # Prompt user or auto-resolve
```

### User Confirmation for System-Wide Changes

Prompt for user confirmation when modifying system config:

```python
from pathlib import Path
from promptrek.adapters.mcp_mixin import MCPGenerationMixin

mixin = MCPGenerationMixin()

system_path = Path.home() / ".config" / "myeditor" / "mcp.json"

# Confirm with user (interactive)
confirmed = mixin.confirm_system_wide_mcp_update(
    editor_name="MyEditor",
    system_path=system_path,
    dry_run=False
)

if confirmed:
    print("User confirmed - proceeding with system-wide update")
    # Update system config...
else:
    print("User declined - skipping MCP configuration")

# In dry run mode, always returns True but shows message
confirmed = mixin.confirm_system_wide_mcp_update(
    editor_name="MyEditor",
    system_path=system_path,
    dry_run=True  # No actual prompt, just shows message
)
```

### Reading Existing Configuration

Read and parse existing MCP configuration:

```python
from pathlib import Path
from promptrek.adapters.mcp_mixin import MCPGenerationMixin

mixin = MCPGenerationMixin()

config_path = Path(".myeditor/mcp.json")

# Read existing config
existing = mixin.read_existing_mcp_config(config_path)

if existing:
    print("Existing configuration found:")
    if "mcpServers" in existing:
        servers = existing["mcpServers"]
        print(f"  MCP servers: {len(servers)}")
        for name in servers:
            print(f"    - {name}")
else:
    print("No existing configuration")
```

### Writing Configuration Files

Write MCP configuration to disk:

```python
from pathlib import Path
from promptrek.adapters.mcp_mixin import MCPGenerationMixin

mixin = MCPGenerationMixin()

config = {
    "mcpServers": {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem"]
        }
    }
}

# Write to file
success = mixin.write_mcp_config_file(
    config=config,
    output_file=Path(".myeditor/mcp.json"),
    dry_run=False,
    verbose=True
)

if success:
    print("Configuration written successfully")

# Dry run mode - preview without writing
mixin.write_mcp_config_file(
    config=config,
    output_file=Path(".myeditor/mcp.json"),
    dry_run=True,  # Don't actually write
    verbose=True   # Show preview
)
```

### Comparing MCP Servers

Compare two MCP server configurations:

```python
from promptrek.adapters.mcp_mixin import MCPGenerationMixin

mixin = MCPGenerationMixin()

server1 = {
    "command": "npx",
    "args": ["-y", "package@1.0.0"],
    "env": {"KEY": "value"}
}

server2 = {
    "command": "npx",
    "args": ["-y", "package@1.0.0"],
    "env": {"KEY": "value"}
}

# Compare
are_different = mixin.compare_mcp_servers(server1, server2)
print(f"Configurations differ: {are_different}")
# Output: False (they're identical)

# Different configurations
server3 = {
    "command": "npx",
    "args": ["-y", "package@2.0.0"]  # Different version
}

are_different = mixin.compare_mcp_servers(server1, server3)
print(f"Configurations differ: {are_different}")
# Output: True (different args)
```

### Prompting for Merge Strategy

Ask user how to handle existing configuration:

```python
from pathlib import Path
from promptrek.adapters.mcp_mixin import MCPGenerationMixin

mixin = MCPGenerationMixin()

config_path = Path(".myeditor/mcp.json")

# Prompt user for strategy
strategy = mixin.prompt_merge_strategy(
    config_file=config_path,
    editor_name="MyEditor"
)

# Handle based on strategy
if strategy == "merge":
    print("Merging MCP servers with existing config")
    # Use merge_mcp_config()
elif strategy == "replace":
    print("Replacing entire config")
    # Overwrite file
elif strategy == "skip":
    print("Skipping MCP generation")
    # Don't generate
elif strategy == "system":
    print("Using system-wide config instead")
    # Use system path
```

### Prompting for Server Overwrite

Ask user about conflicting server configuration:

```python
from promptrek.adapters.mcp_mixin import MCPGenerationMixin

mixin = MCPGenerationMixin()

existing_server = {
    "command": "npx",
    "args": ["-y", "package@1.0.0"]
}

new_server = {
    "command": "npx",
    "args": ["-y", "package@2.0.0"]
}

# Prompt user
should_overwrite = mixin.prompt_mcp_server_overwrite(
    server_name="filesystem",
    existing_config=existing_server,
    new_config=new_server,
    dry_run=False
)

if should_overwrite:
    print("User approved overwrite")
    # Use new configuration
else:
    print("User declined - keeping existing")
    # Keep existing configuration
```

### Warning for User-Level Operations

Warn about user-level (non-project) configuration changes:

```python
from pathlib import Path
from promptrek.adapters.mcp_mixin import MCPGenerationMixin

mixin = MCPGenerationMixin()

user_config_path = Path.home() / ".config" / "myeditor" / "mcp.json"

# Warn user
should_proceed = mixin.warn_user_level_operations(
    editor_name="MyEditor",
    config_path=user_config_path,
    server_count=3,
    dry_run=False
)

if should_proceed:
    print("User confirmed - updating user-level config")
    # Proceed with update
else:
    print("User declined - aborting")
    # Don't update
```

### Configuration Strategy Patterns

Common MCP configuration strategies:

```python
# Project-level configuration (preferred)
{
    "supports_project": True,
    "project_path": ".editor/mcp.json",
    "system_path": None,
    "requires_confirmation": False,
    "config_format": "json"
}

# System-level only (with confirmation)
{
    "supports_project": False,
    "project_path": None,
    "system_path": "~/.config/editor/mcp.json",
    "requires_confirmation": True,
    "config_format": "json"
}

# Hybrid approach (project preferred, system fallback)
{
    "supports_project": True,
    "project_path": ".editor/mcp.json",
    "system_path": "~/.config/editor/mcp.json",
    "requires_confirmation": True,
    "config_format": "json"
}
```

### Variable Substitution in MCP Configuration

Substitute variables in MCP server environment variables:

```python
from promptrek.adapters.mcp_mixin import MCPGenerationMixin
from promptrek.core.models import MCPServer

mixin = MCPGenerationMixin()

servers = [
    MCPServer(
        name="api",
        command="node",
        args=["server.js"],
        env={
            "API_KEY": "{{{ API_KEY }}}",
            "API_URL": "{{{ API_URL }}}",
            "PROJECT_NAME": "{{{ PROJECT_NAME }}}"
        }
    )
]

# Build with variable substitution
config = mixin.build_mcp_servers_config(
    servers,
    variables={
        "API_KEY": "secret-key-123",
        "API_URL": "https://api.example.com",
        "PROJECT_NAME": "my-project"
    }
)

# Result has substituted values:
# {
#     "mcpServers": {
#         "api": {
#             "command": "node",
#             "args": ["server.js"],
#             "env": {
#                 "API_KEY": "secret-key-123",
#                 "API_URL": "https://api.example.com",
#                 "PROJECT_NAME": "my-project"
#             }
#         }
#     }
# }
```

## MCP Configuration Formats

### Standard Format

The standard MCP format used by most editors:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "package"],
      "env": {
        "KEY": "value"
      },
      "description": "Server description"
    }
  }
}
```

All format styles ("standard", "anthropic", "continue") use this same structure.

## See Also

- [Base Adapter](base.md) - Adapter interface
- [MCP Documentation](../../user-guide/mcp/index.md) - Using MCP servers
- [Claude Adapter](../../user-guide/editors/claude.md) - Claude MCP example
- [Cursor Adapter](../../user-guide/editors/cursor.md) - Cursor MCP example
