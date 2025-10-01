# MCP Server Management Guide

## Overview

PrompTrek now supports managing MCP (Model Context Protocol) servers across different AI editors. MCP servers provide additional context and tools to AI editors, enabling capabilities like filesystem access, database queries, web search, and more.

## What is MCP?

The Model Context Protocol (MCP) is a standardized way for AI assistants to connect to external tools and data sources. MCP servers run alongside your AI editor and provide:

- **Tools**: Functions the AI can call (e.g., file operations, API calls)
- **Resources**: Data the AI can access (e.g., files, database schemas)
- **Prompts**: Predefined prompt templates

## Universal MCP Configuration

PrompTrek uses a universal `mcp.promptrek.json` file to define MCP servers that should be available to your project. This file lives in your project root and can be used to generate editor-specific MCP configurations.

### File Location

```
your-project/
├── mcp.promptrek.json          # Universal MCP configuration
├── project.promptrek.yaml       # Your prompt configuration
└── .cursor/                     # Generated editor configs
    └── mcp.json                 # Cursor-specific MCP config
```

### Configuration Format

```json
{
  "schema_version": "1.0.0",
  "metadata": {
    "title": "Project MCP Servers",
    "description": "MCP server configuration for this project",
    "version": "1.0.0",
    "author": "team@example.com"
  },
  "config": {
    "allow_custom_servers": true,
    "require_all_servers": false
  },
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": {
        "API_KEY": "${API_KEY}"
      },
      "description": "Server description",
      "required": false
    }
  }
}
```

## Configuration Options

### `allow_custom_servers`

Controls how PrompTrek handles existing MCP servers in editor configs:

- **`true` (default)**: Merge with existing servers. PrompTrek will:
  - Add new servers from `mcp.promptrek.json`
  - Update servers that match
  - Preserve custom servers not in `mcp.promptrek.json`

- **`false`**: Replace all servers. PrompTrek will:
  - Remove all existing MCP servers
  - Install only servers from `mcp.promptrek.json`
  - Warn before overwriting (unless using `--force`)

### `require_all_servers`

Controls server selection behavior:

- **`false` (default)**: Users can select which servers to install
- **`true`**: All servers must be installed together (no selective installation)

### Server Configuration

Each server in `mcpServers` supports:

- **`command`** (required): Executable to run the server (e.g., `npx`, `node`, `python`)
- **`args`** (optional): Command-line arguments as an array
- **`env`** (optional): Environment variables (supports `${VAR}` substitution)
- **`description`** (optional): Human-readable description
- **`required`** (optional): Whether this server is required for the project

## CLI Usage

### Interactive Mode

Run without options for interactive setup:

```bash
promptrek mcp
```

This will:
1. Auto-detect `mcp.promptrek.json` in current directory
2. Prompt for editor selection (Cursor, Continue, or both)
3. Show available servers with descriptions
4. Prompt for server selection
5. Generate editor-specific configurations

### Non-Interactive Mode

Specify all options on the command line:

```bash
# Generate for Cursor
promptrek mcp --editor cursor

# Generate for multiple editors
promptrek mcp --editor cursor,continue

# Select specific servers
promptrek mcp --editor cursor --server filesystem --server git

# Specify custom MCP file
promptrek mcp --file ./config/mcp.promptrek.json --editor cursor

# Provide variables
promptrek mcp --editor cursor --var GITHUB_TOKEN=ghp_xxx --var API_KEY=secret

# Dry run (see what would be generated)
promptrek mcp --editor cursor --dry-run

# Force overwrite without confirmation
promptrek mcp --editor cursor --force
```

### Command Options

- `--file, -f`: Path to `mcp.promptrek.json` (auto-detects if omitted)
- `--editor, -e`: Target editor(s), comma-separated (e.g., `cursor,continue`)
- `--output, -o`: Output directory (default: current directory)
- `--server, -s`: Select specific server(s) (can be repeated)
- `--dry-run`: Show what would be generated without creating files
- `--force`: Force overwrite without confirmation
- `--var, -V`: Override variables (e.g., `-V API_KEY=value`)
- `--verbose, -v`: Enable verbose output

## Variable Substitution

MCP configurations often need API keys and other sensitive values. PrompTrek supports variable substitution using `${VAR_NAME}` syntax:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

Variables can be provided via:

1. **Environment variables**: Set before running PrompTrek
   ```bash
   export GITHUB_TOKEN=ghp_xxxxx
   promptrek mcp --editor cursor
   ```

2. **Command-line flags**: Pass directly to the command
   ```bash
   promptrek mcp --editor cursor --var GITHUB_TOKEN=ghp_xxxxx
   ```

3. **Interactive prompt**: PrompTrek will prompt for missing required variables (future feature)

## Editor-Specific Formats

### Cursor

PrompTrek generates `.cursor/mcp.json` in Cursor's expected format:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": {
        "API_KEY": "value"
      }
    }
  }
}
```

**Location**: `.cursor/mcp.json` (project-level) or `~/.cursor/mcp.json` (global)

### Continue

PrompTrek updates `config.yaml` with MCP servers in Continue's YAML format:

```yaml
mcpServers:
  - name: server-name
    command: npx
    args:
      - "-y"
      - "package-name"
    env:
      API_KEY: value
```

**Location**: `config.yaml` at project root

## Common MCP Servers

### Filesystem

Provides file read/write access:

```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"],
    "description": "Filesystem access for reading and writing files",
    "required": true
  }
}
```

### Git

Git repository operations:

```json
{
  "git": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-git"],
    "description": "Git operations and version control"
  }
}
```

### GitHub

GitHub API access:

```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
    },
    "description": "GitHub API for issues, PRs, and repositories"
  }
}
```

### Database Servers

PostgreSQL:
```json
{
  "postgres": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/db"],
    "env": {
      "PGPASSWORD": "${DB_PASSWORD}"
    },
    "description": "PostgreSQL database access"
  }
}
```

SQLite:
```json
{
  "sqlite": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sqlite", "/path/to/db.sqlite"],
    "description": "SQLite database access"
  }
}
```

### Web & Search

Brave Search:
```json
{
  "brave-search": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
    "env": {
      "BRAVE_API_KEY": "${BRAVE_API_KEY}"
    },
    "description": "Web search via Brave Search API"
  }
}
```

Fetch (HTTP):
```json
{
  "fetch": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-fetch"],
    "description": "HTTP fetch for web content"
  }
}
```

### Browser Automation

Playwright:
```json
{
  "playwright": {
    "command": "npx",
    "args": ["-y", "@playwright/mcp@latest"],
    "description": "Browser automation with Playwright"
  }
}
```

## Workflows

### Setting Up a New Project

1. Create `mcp.promptrek.json`:
   ```bash
   cat > mcp.promptrek.json << 'EOF'
   {
     "schema_version": "1.0.0",
     "metadata": {
       "title": "My Project MCP Servers",
       "description": "MCP configuration for development"
     },
     "config": {
       "allow_custom_servers": true,
       "require_all_servers": false
     },
     "mcpServers": {
       "filesystem": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
         "description": "Project filesystem access",
         "required": true
       }
     }
   }
   EOF
   ```

2. Generate for your editor:
   ```bash
   promptrek mcp --editor cursor
   ```

3. Restart your AI editor to load MCP servers

### Adding a New Server

1. Edit `mcp.promptrek.json` to add the server
2. Regenerate configurations:
   ```bash
   promptrek mcp --editor cursor,continue
   ```
3. Restart editors

### Team Configuration

For teams, commit `mcp.promptrek.json` to version control:

```bash
git add mcp.promptrek.json
git commit -m "feat: add MCP server configuration"
```

Team members can then run:
```bash
promptrek mcp --editor cursor
```

**Note**: Do NOT commit editor-specific MCP files (`.cursor/mcp.json`, `config.yaml`). Add them to `.gitignore`:

```gitignore
# Editor MCP configs (generated by PrompTrek)
.cursor/mcp.json
config.yaml
```

### Environment-Specific Servers

Use variables for environment-specific configuration:

```json
{
  "mcpServers": {
    "database": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "${DATABASE_URL}"],
      "env": {
        "PGPASSWORD": "${DB_PASSWORD}"
      }
    }
  }
}
```

Development:
```bash
export DATABASE_URL=postgresql://localhost/dev
promptrek mcp --editor cursor
```

Production:
```bash
export DATABASE_URL=postgresql://prod-host/prod
promptrek mcp --editor cursor
```

## Troubleshooting

### MCP Servers Not Loading

1. Check editor console for errors
2. Verify server is installed: `npm list -g @modelcontextprotocol/server-*`
3. Test server manually: `npx -y @modelcontextprotocol/server-filesystem .`
4. Restart editor after generating configs

### Missing Variables

Error: `Missing required environment variables: GITHUB_TOKEN`

Solution:
```bash
export GITHUB_TOKEN=ghp_xxxxx
# Or
promptrek mcp --editor cursor --var GITHUB_TOKEN=ghp_xxxxx
```

### Permission Denied

Some servers (like filesystem) need specific permissions:

```json
{
  "filesystem": {
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/absolute/path"]
  }
}
```

Use absolute paths and ensure the directory exists.

### Servers Overwritten

If `allow_custom_servers: false` and you have custom servers:

1. Set `allow_custom_servers: true` in `mcp.promptrek.json`
2. Regenerate: `promptrek mcp --editor cursor`

Or move custom servers to `mcp.promptrek.json`.

## Best Practices

1. **Version Control**: Commit `mcp.promptrek.json`, not generated configs
2. **Security**: Never commit API keys; use variables and `.env` files
3. **Documentation**: Add descriptions to help team understand server purposes
4. **Required Servers**: Mark essential servers as `required: true`
5. **Testing**: Use `--dry-run` to preview changes before applying
6. **Environment**: Use `.env` files for local development variables

## Examples

See [examples/mcp.promptrek.json](../examples/mcp.promptrek.json) for a complete example with multiple server types.

## Further Reading

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Cursor MCP Documentation](https://docs.cursor.com/context/model-context-protocol)
- [Continue MCP Documentation](https://docs.continue.dev/customize/deep-dives/mcp)
- [Official MCP Servers](https://github.com/modelcontextprotocol)
