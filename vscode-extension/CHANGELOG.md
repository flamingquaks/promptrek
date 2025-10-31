# Changelog

All notable changes to the PrompTrek VSCode extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-XX

### Added
- Initial release of PrompTrek VSCode extension
- Configuration Explorer tree view showing:
  - Current configuration file
  - Metadata section
  - Variables section
  - Content preview
  - Plugins (MCP servers, commands, agents, hooks)
  - Documents section
- Editor Status tree view showing:
  - All supported editors
  - Generation status for each editor
  - One-click generation capability
- All PrompTrek CLI commands integrated:
  - Initialize configuration with templates
  - Generate for specific or all editors
  - Validate configuration (normal and strict modes)
  - Preview output before generation
  - Sync from editor files to PrompTrek format
  - Migrate schema versions
  - Plugin management (list, generate, validate)
  - Pre-commit hooks installation
  - .gitignore configuration
- Context menus for `.promptrek.yaml` files:
  - Validate
  - Generate for editor
  - Generate for all editors
  - Open in editor
- Status bar integration:
  - Shows current schema version
  - Click to open configuration
  - Configurable visibility
- Auto-validation on save (configurable)
- File system watcher for automatic view refresh
- Interactive wizards for all commands with user-friendly prompts
- Variable override support during generation
- Headless mode support for autonomous agents
- Output channel for CLI command results
- Welcome message for first-time users
- Extension settings:
  - CLI path configuration
  - Auto-validation toggle
  - Default schema version
  - Status bar visibility

### Documentation
- Comprehensive README with usage examples
- Feature descriptions and screenshots
- Troubleshooting guide
- Configuration reference
- Command reference

## [Unreleased]

### Planned Features
- Webview-based configuration editor
- Inline YAML validation and autocompletion
- Diff view for sync operations
- Configuration templates browser
- Plugin marketplace integration
- Real-time preview panel
- Multi-workspace support
- Configuration snippets
- Visual MCP server builder
- Agent testing interface
- Export/import configurations
- Configuration backup/restore
- Integration with VSCode settings sync

[0.1.0]: https://github.com/flamingquaks/promptrek/releases/tag/vscode-v0.1.0
