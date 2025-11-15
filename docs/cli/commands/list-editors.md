# promptrek list-editors

List all available AI editor adapters.

## Synopsis

```bash
promptrek list-editors [OPTIONS]
```

## Description

The `list-editors` command displays all AI editors supported by PrompTrek, along with their capabilities and configuration methods.

## Options

**`-v, --verbose`**
: Show detailed information about each editor

## Examples

### Basic List

```bash
$ promptrek list-editors

Available AI Editors:
  • claude - Claude Code editor
  • continue - Continue VSCode extension
  • cursor - Cursor IDE
  • cline - Cline extension
  • windsurf - Windsurf IDE
  • amazon-q - Amazon Q Developer
  • kiro - Kiro editor
  • copilot - GitHub Copilot (global config only)
  • jetbrains - JetBrains AI Assistant (global config only)
```

### Verbose Output

```bash
$ promptrek list-editors --verbose

Available AI Editors:

claude - Claude Code editor
  Support Level: Full
  Configuration: Project-level (.claude/)
  MCP Support: Yes (project-level)
  Multi-Document: Yes
  Plugins: Commands, Agents, Hooks, MCP Servers

continue - Continue VSCode extension
  Support Level: Full
  Configuration: Project-level (.continue/)
  MCP Support: Yes (project-level)
  Multi-Document: Yes
  Plugins: Commands, MCP Servers

cursor - Cursor IDE
  Support Level: Full
  Configuration: Project-level (.cursorrules, .cursor/)
  MCP Support: Yes (project-level)
  Multi-Document: Yes
  Plugins: MCP Servers

cline - Cline extension
  Support Level: Partial
  Configuration: Project-level (.cline/)
  MCP Support: Via VSCode settings
  Multi-Document: Yes

windsurf - Windsurf IDE
  Support Level: Full
  Configuration: System-wide only
  MCP Support: Yes (system-wide)
  Multi-Document: Yes
  Plugins: MCP Servers

amazon-q - Amazon Q Developer
  Support Level: Full
  Configuration: Project-level (.amazonq/)
  MCP Support: Yes (project-level)
  Multi-Document: Yes
  Plugins: Commands, Agents, CLI Agents, MCP Servers

kiro - Kiro editor
  Support Level: Full
  Configuration: Project-level (.kiro/)
  MCP Support: Yes (project-level)
  Multi-Document: Yes
  Plugins: MCP Servers

copilot - GitHub Copilot
  Support Level: Informational
  Configuration: Global (GitHub settings)
  MCP Support: No
  Multi-Document: No (single instruction file)
  Note: Configure through GitHub settings, not project files

jetbrains - JetBrains AI Assistant
  Support Level: Informational
  Configuration: IDE-specific
  MCP Support: No
  Multi-Document: Limited
  Note: Configure through IDE preferences
```

## Output Fields

### Editor Name

The identifier used with `--editor` flag:

```bash
# Use the editor name with generate command
promptrek generate --editor claude
promptrek generate --editor cursor
```

### Support Level

- **Full**: Complete PrompTrek support with file generation
- **Partial**: Basic support, limited features
- **Informational**: Shows usage instructions, no file generation

### Configuration Method

Where the editor stores its configuration:

- **Project-level**: Files in project directory (committed or gitignored)
- **System-wide**: User's home directory or global config
- **Global**: Platform-wide settings (e.g., GitHub)
- **IDE-specific**: Within IDE preferences

### MCP Support

Model Context Protocol server support:

- **Yes (project-level)**: Can configure MCP servers per-project
- **Yes (system-wide)**: MCP servers configured globally
- **Via ...**: Indirect support through another mechanism
- **No**: No MCP support

### Multi-Document Support

Whether the editor supports multiple prompt documents:

- **Yes**: Can use PrompTrek's `documents` array
- **Limited**: Basic multi-file support
- **No**: Single file only

### Plugin Support

Which PrompTrek plugin types are supported:

- **Commands**: Slash commands
- **Agents**: Autonomous agents
- **Hooks**: Event-driven automation
- **MCP Servers**: Model Context Protocol servers
- **CLI Agents**: Command-line agents (Amazon Q specific)

## Editor Categories

### Project-Level Editors

Generate files in project directory:

- **claude**: `.claude/prompts/`, `.claude/mcp.json`
- **continue**: `.continue/config.json`
- **cursor**: `.cursorrules`, `.cursor/`
- **cline**: `.cline/prompts/`
- **amazon-q**: `.amazonq/`
- **kiro**: `.kiro/`

**Usage**:
```bash
promptrek generate --editor claude
# Creates .claude/ directory in project
```

### System-Wide Editors

Configure in user's home directory:

- **windsurf**: `~/.codeium/windsurf/mcp_config.json`

**Usage**:
```bash
promptrek generate --editor windsurf
# Prompts before modifying system-wide config
```

### Informational Editors

Show configuration instructions:

- **copilot**: Configure via GitHub settings
- **jetbrains**: Configure via IDE preferences

**Usage**:
```bash
promptrek generate --editor copilot
# Shows instructions, doesn't generate files
```

## Use Cases

### Choosing an Editor

List editors to decide which to use:

```bash
# See all options
promptrek list-editors

# Get details to compare
promptrek list-editors --verbose
```

### Verifying Support

Check if an editor supports needed features:

```bash
$ promptrek list-editors --verbose | grep -A 10 "amazon-q"

amazon-q - Amazon Q Developer
  Support Level: Full
  Configuration: Project-level (.amazonq/)
  MCP Support: Yes (project-level)
  Multi-Document: Yes
  Plugins: Commands, Agents, CLI Agents, MCP Servers
```

### Integration Documentation

Get editor-specific information for documentation:

```bash
# Export editor list
promptrek list-editors > editors.txt

# Export detailed info
promptrek list-editors --verbose > editors-detailed.txt
```

## Editor Selection Guide

### For Teams (Project-Level Preferred)

Best for teams needing consistent, version-controlled setup:

1. **Claude Code** - Full featured, project-level
2. **Cursor** - Popular, project-level
3. **Continue** - VSCode extension, project-level
4. **Amazon Q** - AWS integration, project-level

```bash
promptrek generate --all
# Generates for all project-level editors
```

### For Individual Use

Editors with system-wide configuration:

1. **Windsurf** - System-wide only
2. **GitHub Copilot** - Global configuration

```bash
promptrek generate --editor windsurf
```

### For Plugin Developers

Editors with best plugin support:

1. **Claude** - All plugin types
2. **Amazon Q** - CLI agents support
3. **Continue** - Commands and MCP

## Adapter Capabilities

### Full Feature Support

Editors supporting all PrompTrek features:

- Claude Code
- Cursor (most features)
- Continue
- Amazon Q
- Windsurf
- Kiro

### Basic Support

Editors with limited feature support:

- Cline (prompts only)
- GitHub Copilot (single instruction file)
- JetBrains (IDE-dependent)

## See Also

- [Generate Command](generate.md) - Generate for specific editor
- [Adapter Capabilities](../../user-guide/adapters/capabilities.md) - Detailed capabilities
- [Adapters Overview](../../user-guide/adapters/index.md) - Adapter documentation
