# PrompTrek VSCode Extension

[![VSCode Extension CI](https://github.com/flamingquaks/promptrek/actions/workflows/vscode-extension-ci.yml/badge.svg)](https://github.com/flamingquaks/promptrek/actions/workflows/vscode-extension-ci.yml)
[![VSCode Extension Release](https://github.com/flamingquaks/promptrek/actions/workflows/vscode-extension-release.yml/badge.svg)](https://github.com/flamingquaks/promptrek/actions/workflows/vscode-extension-release.yml)

A Visual Studio Code extension that provides a user-friendly interface for [PrompTrek](https://github.com/flamingquaks/promptrek), the universal AI editor configuration management tool.

## Features

### 🎯 Visual Configuration Management

- **Explorer View**: Browse your PrompTrek configuration with an intuitive tree view
  - View metadata, variables, content, plugins, and documents
  - Quick access to MCP servers, custom commands, agents, and event hooks
  - Real-time updates when configuration changes

- **Editor Status View**: See which editors have generated configurations
  - One-click generation for any supported editor
  - Visual indicators for generated vs. not-generated editors
  - Supports all PrompTrek-compatible editors

### ⚡ Quick Actions

All PrompTrek CLI commands accessible through VSCode:

- **Initialize**: Create new PrompTrek configurations with templates
- **Generate**: Create editor-specific files (GitHub Copilot, Cursor, Continue, Claude Code, etc.)
- **Validate**: Check your configuration for errors
- **Preview**: See generated output before creating files
- **Sync**: Import editor files back to PrompTrek format
- **Migrate**: Upgrade schema versions

### 🎨 Context Menus

Right-click on `.promptrek.yaml` files for quick access to:
- Validate configuration
- Generate for specific editor
- Generate for all editors
- Open configuration editor

### 🔧 Smart Features

- **Auto-validation**: Automatically validate on save (configurable)
- **Status Bar**: Shows current configuration and schema version
- **File Watcher**: Automatically refreshes views when files change
- **Variable Overrides**: Interactive prompts for variable customization
- **Plugin Management**: Easy management of MCP servers, commands, agents, and hooks

## ⚠️ Requirements - READ THIS FIRST!

**IMPORTANT:** This extension is a **graphical wrapper** around the PrompTrek CLI. You **MUST** install the CLI first!

### 1. Visual Studio Code 1.85.0 or higher

### 2. PrompTrek CLI **REQUIRED**

The extension will **NOT work** without the PrompTrek CLI installed and available in your PATH.

**Quick Install:**
```bash
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek
uv sync  # or: pip install -e .
source .venv/bin/activate  # Unix/Mac
# OR: .venv\Scripts\activate  # Windows
```

**Verify it's installed:**
```bash
promptrek --version
# Should output: PrompTrek version 0.6.0
```

**If you get "command not found" errors in the extension:**
- See [CLI-SETUP.md](CLI-SETUP.md) for detailed installation instructions
- Make sure `promptrek` command works in your terminal first
- You may need to configure the CLI path in VSCode settings

## Installation

### From Source

1. Clone the PrompTrek repository:
   ```bash
   git clone https://github.com/flamingquaks/promptrek.git
   cd promptrek/vscode-extension
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Compile the extension:
   ```bash
   npm run compile
   ```

4. Open in VSCode and press F5 to launch Extension Development Host

### From VSIX (Coming Soon)

The extension will be available on the VSCode Marketplace soon.

## Getting Started

1. **Open a workspace** containing a PrompTrek configuration or start fresh

2. **Initialize a configuration**:
   - Click the "Initialize Configuration" button in the PrompTrek sidebar
   - Or use Command Palette: `PrompTrek: Initialize Configuration`
   - Follow the interactive prompts to set up your configuration

3. **Generate editor files**:
   - In the "Supported Editors" view, click on any editor to generate its configuration
   - Or use Command Palette: `PrompTrek: Generate for Editor...`
   - Choose specific editors or generate for all at once

4. **Manage your configuration**:
   - Browse your configuration in the tree view
   - Edit the `.promptrek.yaml` file directly
   - Use validation to check for errors

## Configuration

The extension can be configured through VSCode settings:

```json
{
  "promptrek.cliPath": "promptrek",
  "promptrek.autoValidate": true,
  "promptrek.defaultSchemaVersion": "3.1.0",
  "promptrek.showStatusBar": true
}
```

### Settings

- `promptrek.cliPath`: Path to PrompTrek CLI executable (default: `"promptrek"`)
- `promptrek.autoValidate`: Automatically validate `.promptrek.yaml` files on save (default: `true`)
- `promptrek.defaultSchemaVersion`: Default schema version for new configurations (default: `"3.1.0"`)
- `promptrek.showStatusBar`: Show PrompTrek status in the status bar (default: `true`)

## Supported Editors

The extension supports all PrompTrek-compatible editors:

- ✅ **GitHub Copilot** - Repository-wide instructions
- ✅ **Cursor** - Modern rules system with metadata
- ✅ **Continue** - Organized markdown rules
- ✅ **Claude Code** - Rich context with full plugin ecosystem
- ✅ **Windsurf** - AI-powered coding assistance
- ✅ **Cline** - VSCode autonomous AI agent
- ✅ **Kiro** - Comprehensive steering system
- ✅ **Amazon Q** - Rules and CLI agents
- ✅ **JetBrains AI** - IDE-integrated assistance

## Commands

All commands are available through the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`):

- `PrompTrek: Initialize Configuration` - Create new configuration
- `PrompTrek: Validate Configuration` - Validate current configuration
- `PrompTrek: Generate for Editor...` - Generate for specific editor
- `PrompTrek: Generate for All Editors` - Generate for all supported editors
- `PrompTrek: Preview Output...` - Preview generated output
- `PrompTrek: Sync from Editor Files...` - Import from editor files
- `PrompTrek: Migrate Schema Version...` - Upgrade schema version
- `PrompTrek: Refresh View` - Refresh tree views
- `PrompTrek: Open Configuration File` - Open main config file
- `PrompTrek: Install Pre-commit Hooks` - Set up git hooks
- `PrompTrek: Configure .gitignore` - Manage ignored files
- `PrompTrek: List Plugins` - Show all configured plugins
- `PrompTrek: Generate Plugins for Editor...` - Generate plugin files

## Usage Examples

### Creating a New Configuration

1. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Type "PrompTrek: Initialize Configuration"
3. Follow the prompts:
   - Choose output file name
   - Select schema version (v3.1.0 recommended)
   - Optionally select a template (React, Node, Python)
   - Choose whether to set up pre-commit hooks

### Generating for Specific Editor

1. In the "Supported Editors" view, click on an editor (e.g., "Cursor")
2. Or use Command Palette: `PrompTrek: Generate for Editor...`
3. Optionally add variable overrides
4. Configuration files are created automatically

### Validating Configuration

1. Right-click on a `.promptrek.yaml` file in the Explorer
2. Select "Validate Configuration"
3. Choose validation mode (normal or strict)
4. View results in notification or output panel

## Troubleshooting

### Extension Can't Find PrompTrek CLI

Make sure PrompTrek is installed and in your PATH:
```bash
which promptrek  # Unix/Mac
where promptrek  # Windows
```

If not in PATH, set the full path in settings:
```json
{
  "promptrek.cliPath": "/full/path/to/promptrek"
}
```

### Configuration Not Detected

The extension looks for `.promptrek.yaml` files in your workspace. Make sure:
- The file has the correct extension (`.promptrek.yaml`)
- The file is in your workspace folder
- Use "Refresh View" command if needed

### Validation Errors

Check the PrompTrek output channel for detailed error messages:
- View → Output
- Select "PrompTrek" from the dropdown

## Development & CI/CD

The extension uses automated GitHub Actions workflows for continuous integration and releases.

### Automated Workflows

- **CI Pipeline**: Runs on every PR and commit
  - Tests on Ubuntu, Windows, macOS
  - Tests with Node.js 18.x and 20.x
  - Linting, compilation, and package validation
  - Security scanning with npm audit and TruffleHog

- **Release Pipeline**: Triggered by version tags
  - Builds platform-specific VSIX packages
  - Creates GitHub releases with artifacts
  - Optionally publishes to VSCode Marketplace and Open VSX

- **PR Packaging**: Automatically packages extension for review
  - Creates VSIX artifact for each PR
  - Comments on PR with installation instructions
  - Analyzes bundle size and dependencies

### For Developers

See comprehensive documentation:
- [Workflows Guide](.github/WORKFLOWS.md) - CI/CD setup and usage
- [Release Guide](RELEASE.md) - Step-by-step release process
- [Contributing Guide](CONTRIBUTING.md) - Development guidelines

### Building Locally

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch mode for development
npm run watch

# Lint code
npm run lint

# Package extension
npm install -g @vscode/vsce
vsce package
```

## Contributing

Contributions are welcome! Please see the [main PrompTrek repository](https://github.com/flamingquaks/promptrek) for contribution guidelines.

## License

MIT License - see the [LICENSE](../LICENSE) file for details.

## Resources

- [PrompTrek Documentation](https://flamingquaks.github.io/promptrek)
- [GitHub Repository](https://github.com/flamingquaks/promptrek)
- [Issue Tracker](https://github.com/flamingquaks/promptrek/issues)
- [Quick Start Guide](https://flamingquaks.github.io/promptrek/quick-start.html)

## Changelog

### 0.1.0 (Initial Release)

- ✨ Initial release of PrompTrek VSCode extension
- 📊 Configuration explorer tree view
- 📝 Editor status view with generation status
- ⚡ All PrompTrek CLI commands integrated
- 🎨 Context menus for quick actions
- 🔧 Auto-validation on save
- 📍 Status bar integration
- 🔄 File system watcher for live updates
- 🎯 Interactive configuration wizard
- 📦 Plugin management support
