# PrompTrek Documentation

<div align="center">
  <img src="assets/promptrek-logo-with-text.png" alt="PrompTrek" width="400">

  **Taking your AI editor configurations on a journey across every platform!**
</div>

## Welcome to PrompTrek

PrompTrek is a universal configuration solution that takes your prompts, MCP servers, custom commands, autonomous agents, and event hooks on a journey across every AI editor. Define your complete AI editor setup once in a standardized format, then PrompTrek automatically generates optimized configurations for GitHub Copilot, Cursor, Continue, Claude Code, and more.

## 🎯 What Problem Does PrompTrek Solve?

AI coding assistants like GitHub Copilot, Cursor, Continue, and others all use different prompt formats and configuration methods. When working across teams or switching between editors, you have to maintain separate prompt configurations for each tool.

PrompTrek solves this by:

- **Universal Format**: Create prompts once in a standardized format (now with **schema v3.1.0** - cleaner architecture!)
- **Multi-Editor Support**: Generate prompts for any supported AI editor automatically
- **Bidirectional Sync**: Parse editor files back to `.promptrek.yaml` without data loss
- **Plugin Ecosystem**: Configure MCP servers, custom commands, autonomous agents, and event hooks
- **Auto .gitignore Management**: Automatically exclude generated editor files from version control
- **Team Consistency**: Share prompt configurations across team members regardless of their editor choice
- **Easy Migration**: Switch between AI editors without losing your prompt configurations

## 🚀 Quick Start

Get started with PrompTrek in just a few minutes:

```bash
# Install from source
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek
uv sync

# Create your first prompt
uv run promptrek init --template react --output my-project.promptrek.yaml

# Generate for all editors
uv run promptrek generate my-project.promptrek.yaml --all
```

See the [Quick Start Guide](getting-started/quick-start.md) for detailed instructions.

## 📚 Documentation Sections

### [Getting Started](getting-started/quick-start.md)
Learn how to install PrompTrek, create your first configuration, and generate editor-specific prompts.

### [User Guide](user-guide/index.md)
Comprehensive guide covering the UPF specification, configuration options, advanced features, and all supported editor adapters.

### [CLI Reference](cli/index.md)
Complete command-line interface reference with detailed documentation for all commands and options.

### [Examples](examples/index.md)
Real-world examples ranging from basic React apps to complex microservices architectures, including plugin configurations.

### [Developer Guide](developer/index.md)
Learn about PrompTrek's architecture, development setup, testing, and how to contribute.

### [API Reference](api/index.md)
Detailed API documentation for core modules, adapters, and utilities.

### [Schema Reference](schema/index.md)
JSON Schema documentation for all PrompTrek configuration formats (v1.0 through v3.1).

## 🎨 Supported Editors

PrompTrek supports all major AI coding assistants:

| Editor | Status | Config Location |
|--------|--------|-----------------|
| **GitHub Copilot** | ✅ Full Support | `.github/copilot-instructions.md` |
| **Cursor** | ✅ Full Support | `.cursor/rules/*.mdc` |
| **Claude Code** | ✅ Full Support | `.claude/CLAUDE.md` |
| **Continue** | ✅ Full Support | `.continue/rules/*.md` |
| **Windsurf** | ✅ Full Support | `.windsurf/rules/*.md` |
| **Cline** | ✅ Full Support | `.clinerules/*.md` |
| **Kiro** | ✅ Full Support | `.kiro/steering/*.md` |
| **Amazon Q** | ✅ Full Support | `.amazonq/rules/*.md` |
| **JetBrains AI** | ✅ Full Support | `.assistant/rules/*.md` |

See the [Editor Adapters](user-guide/adapters/index.md) section for detailed information about each adapter.

## 🔌 Plugin Support

Configure MCP servers, custom commands, autonomous agents, and event hooks with clean top-level fields:

```yaml
schema_version: "3.1.0"
metadata:
  title: "My Project"

# Plugin configurations
mcp_servers:
  - name: github
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]

commands:
  - name: review-code
    description: "Review code for quality"
    prompt: "Review the selected code..."

agents:
  - name: test-generator
    description: "Generate unit tests"
    prompt: "Generate comprehensive tests..."
```

Learn more in the [Plugins Guide](user-guide/plugins/index.md).

## 🤝 Contributing

We welcome contributions! Check out our [Contributing Guide](community/contributing.md) to get started.

## 📄 License

PrompTrek is licensed under the MIT License. See the [LICENSE](https://github.com/flamingquaks/promptrek/blob/main/LICENSE) file for details.

## 🔗 Links

- [GitHub Repository](https://github.com/flamingquaks/promptrek)
- [Issue Tracker](https://github.com/flamingquaks/promptrek/issues)
- [Changelog](reference/changelog.md)
- [FAQ](reference/faq.md)
