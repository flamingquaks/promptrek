# Changelog

All notable changes to PrompTrek are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

!!! note "Version Numbering"
    PrompTrek has two version numbers:

    - **Application Version** - The version of the PrompTrek tool itself (e.g., v0.5.0)
    - **Schema Version** - The configuration format version (e.g., v3.1.0)

    This changelog tracks the application version. For schema changes, see the [V3 Migration Guide](../V3_MIGRATION_GUIDE.md).

## [Unreleased]

### Features
- Add interactive CLI wizard with guided workflows
- Update release script to include uv.lock versioning

### Bug Fixes
- Claude editor sync command bug

## [0.5.0] - 2025-10-27

### Features
- **Dynamic Variables System** - Built-in and command-based dynamic variables
  - Built-in variables: CURRENT_DATE, CURRENT_TIME, CURRENT_DATETIME, CURRENT_YEAR, CURRENT_MONTH, CURRENT_DAY, PROJECT_NAME, PROJECT_ROOT, GIT_BRANCH, GIT_COMMIT_SHORT
  - User-defined command-based variables via `.promptrek/variables.promptrek.yaml`
  - `allow_commands` field for security control
  - Variable caching mechanism
  - `promptrek refresh` command to regenerate with updated variables
  - Generation metadata (`.promptrek/last-generation.yaml`)
  - .gitignore and pre-commit hooks for metadata files

## [0.4.0] - 2025-10-26

### Features
- **Automatic PR Labeling** - GitHub Actions workflow for PR labeling based on changed files
- **Claude-Specific .gitignore** - Patterns for Claude editor files
- **Cline MCP Improvements** - Enhanced MCP support and variable refactoring
- **JSON Schema Publishing** - Published schemas for UPF v2.0, v2.1, and v3.0
- **Cline VSCode Integration** - Enhanced Cline adapter with VSCode support
- **Continue Modular Configuration** - Improved Continue adapter with modular config
- **Enhanced UPF Schemas** - Better content handling and descriptions

### Bug Fixes
- SAFETY_API_KEY environment variable handling
- Claude missing project agents
- Cursor adapter and UPF models with metadata support
- Improved adapter alignment with their editors
- Continue IDE file generation and documentation
- Website layout and responsiveness
- Safety scan output handling and error management
- Python version in security workflow (3.12)
- YAML schemas to include major.minor.patch in URL

## [0.3.1] - 2025-10-17

### Features
- **v3.0.0 Schema Support** - Full support for schema v3.0.0
- Documentation and configuration updates for v3.0.0
- New .gitignore entries for v3.0 files
- Migration instructions for v2.x to v3.0

## [0.3.0] - 2025-10-16

### Features
- **UniversalPromptV3 Support** - New schema version with top-level plugin fields
- **Enhanced Migration Functionality** - Automated migration from v2.x to v3.0
- **.gitignore Configuration** - Editor-specific file management
- **V3 Documentation** - Migration guide and deprecation warnings

### Breaking Changes
- Schema v3.0 moves plugins to top-level (backward compatible)

## [0.2.0] - 2025-10-15

### Features
- **v2.1 Plugin Support** - MCP servers, commands, agents, hooks
- Enhanced configurations for all editors

### Bug Fixes
- PyYAML dependency version downgrade to 5.4
- Keywords and dependency cleanup

## [0.1.1] - 2025-10-13

### Features
- **Enhanced Changelog Generation** - Last stable version detection

### Bug Fixes
- Changelog sections and entry ordering
- Hook stages updated to pre-commit

## [0.0.7] - 2025-10-08

### Features
- **Local Variables File** - Support for `.promptrek/variables.promptrek.yaml`
- Prevent accidental commits of variables

### Bug Fixes
- Sync support across editors
- Cline file name (.cline_rules.md to .clinerules/context.md)

## [0.0.6] - 2025-10-01

### Bug Fixes
- Pre-commit hook arguments
- Removed Windsurf references

## [0.0.3] - 2025-10-01

### Features
- **Pre-commit Hooks Integration** - Automated validation and prevention
- **Preview Command** - Generate output previews without writing files

### Bug Fixes
- Release notes generation with fallback
- Duplicate permissions declaration in CI

## [0.0.2] - 2025-09-29

Initial public release.

## [0.0.1] - 2025-09-29

### Features
- **Agent Instructions** - Persistent agent instruction files
- **Bidirectional Sync** - Create/update PrompTrek from editor files
- **GitHub Actions Workflows** - Automated testing and CI/CD
- **Release Scripts** - Version management and tagging
- **Security Workflows** - Reusable security scanning
- **Multi-File Support** - Multiple prompt files with intelligent merging
- **Conventional Commits** - Automated changelog generation

### Bug Fixes
- GitHub Pages CSS loading
- Test and validation failures
- Safety scan condition for -rc tags

## [0.0.0-rc.6] through [0.0.0-rc.1] - 2025-09-29

Release candidate versions with iterative improvements.

### Features (Across RC Versions)
- **Core Functionality** - Agent Prompt Mapper (Phases 1-3)
- **Adapter Architecture** - Variable substitution and 6 editor adapters
- **Advanced Templates** - Complete adapter implementations
- **Editor Support** - GitHub Copilot, Cursor, Continue, Kiro, Cline, Claude Code, Windsurf, Amazon Q, JetBrains AI
- **Kiro Adapter** - Hooks and prompts systems
- **Release Workflow** - Differentiation between regular and pre-release

### Bug Fixes (Across RC Versions)
- Claude files and CI build issues
- Safety API key configuration
- GitHub Pages domain configuration
- Test matrix workflow failures
- Copilot file generation
- Python <3.9 compatibility
- UV build issues

### Breaking Changes
- **Python 3.8 Dropped** - Minimum version is now Python 3.9

## Version History Summary

| Version | Release Date | Highlights |
|---------|--------------|------------|
| 0.5.0 | 2025-10-27 | Dynamic variables system |
| 0.4.0 | 2025-10-26 | Schema v3.0, MCP improvements, PR labeling |
| 0.3.1 | 2025-10-17 | v3.0.0 schema support |
| 0.3.0 | 2025-10-16 | UniversalPromptV3, migration tools |
| 0.2.0 | 2025-10-15 | v2.1 plugin support |
| 0.1.1 | 2025-10-13 | Enhanced changelog |
| 0.0.7 | 2025-10-08 | Local variables support |
| 0.0.3 | 2025-10-01 | Pre-commit hooks, preview |
| 0.0.1 | 2025-09-29 | Initial public release |

## Schema Version History

For details on schema version changes:

| Schema Version | Released | Features |
|----------------|----------|----------|
| v3.1.0 | Current | Refined agent model, workflow support |
| v3.0.0 | 2025-10-16 | Top-level plugins, cleaner architecture |
| v2.1.0 | 2025-10-15 | Nested plugins (mcp_servers, commands, agents, hooks) |
| v2.0.0 | Initial | Multi-document support |
| v1.0.0 | Initial | Basic prompt format |

See [V3 Migration Guide](../V3_MIGRATION_GUIDE.md) for migration details.

## Links

- **GitHub Releases**: [https://github.com/flamingquaks/promptrek/releases](https://github.com/flamingquaks/promptrek/releases)
- **Full Changelog**: [https://github.com/flamingquaks/promptrek/blob/main/CHANGELOG.md](https://github.com/flamingquaks/promptrek/blob/main/CHANGELOG.md)
- **Issues**: [https://github.com/flamingquaks/promptrek/issues](https://github.com/flamingquaks/promptrek/issues)
- **Discussions**: [https://github.com/flamingquaks/promptrek/discussions](https://github.com/flamingquaks/promptrek/discussions)

[Unreleased]: https://github.com/flamingquaks/promptrek/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/flamingquaks/promptrek/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/flamingquaks/promptrek/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/flamingquaks/promptrek/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/flamingquaks/promptrek/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/flamingquaks/promptrek/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/flamingquaks/promptrek/compare/v0.0.7...v0.1.1
[0.0.7]: https://github.com/flamingquaks/promptrek/compare/v0.0.6...v0.0.7
[0.0.6]: https://github.com/flamingquaks/promptrek/compare/v0.0.5...v0.0.6
[0.0.3]: https://github.com/flamingquaks/promptrek/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/flamingquaks/promptrek/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/flamingquaks/promptrek/releases/tag/v0.0.1
