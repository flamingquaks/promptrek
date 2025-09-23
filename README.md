# Agent Prompt Mapper

A universal AI Editor prompt storage solution that dynamically maps prompt data to a wide-range of agentic/AI editors and tools. This tool allows you to create generic prompts and workflows in a standardized format, then generate editor-specific prompts for your preferred AI coding assistant.

## 🎯 Problem It Solves

AI coding assistants like GitHub Copilot, Cursor, Continue, and others all use different prompt formats and configuration methods. When working across teams or switching between editors, you have to maintain separate prompt configurations for each tool. Agent Prompt Mapper solves this by:

- **Universal Format**: Create prompts once in a standardized format
- **Multi-Editor Support**: Generate prompts for any supported AI editor
- **Team Consistency**: Share prompt configurations across team members regardless of their editor choice
- **Easy Migration**: Switch between AI editors without losing your prompt configurations

## 🚀 Quick Example

1. Create a universal prompt file (`.apm.yaml`):
```yaml
schema_version: "1.0.0"
metadata:
  title: "My Project Assistant"
  description: "AI assistant for React TypeScript project"
targets: [copilot, cursor, continue]
instructions:
  general:
    - "Use TypeScript for all new files"
    - "Follow React functional component patterns"
    - "Write comprehensive tests"
```

2. Generate editor-specific prompts:
```bash
# Generate for GitHub Copilot
apm generate --editor copilot

# Generate for Cursor
apm generate --editor cursor

# Generate for all configured editors
apm generate --all
```

3. Use the generated prompts in your preferred editor!

## 📋 Project Status

This project is currently in **active development** with core functionality implemented and working. Current status:

- ✅ **Core Functionality Complete**: UPF parser, validation, and CLI interface
- ✅ **Multi-Editor Support**: GitHub Copilot, Cursor, and Continue editors implemented
- ✅ **Template System**: Built-in templates for common project types
- ✅ **Comprehensive Testing**: 41 tests covering unit and integration scenarios
- ✅ **Documentation**: Getting Started guide and comprehensive CLI help
- ⏳ **Advanced Features**: Variable substitution, conditional templates, more editors

**Ready for use!** The tool can create, validate, and generate editor-specific prompts for the three major AI editors.

## 📖 Documentation

All planning documents are available in the [`docs/`](./docs/) directory:

- [Project Planning](./docs/PLANNING.md) - Overall project goals and requirements
- [Editor Research](./docs/EDITOR_RESEARCH.md) - Research on different AI editors
- [System Architecture](./docs/ARCHITECTURE.md) - Technical architecture and design
- [Universal Prompt Format](./docs/UPF_SPECIFICATION.md) - Complete format specification
- [Implementation Roadmap](./docs/IMPLEMENTATION_ROADMAP.md) - Development timeline and phases
- [Project Structure](./docs/PROJECT_STRUCTURE.md) - Repository organization and conventions

## 🎨 Supported Editors

### ✅ Implemented
- **GitHub Copilot** - `.github/copilot-instructions.md` - Full project context, instructions, examples
- **Cursor** - `.cursorrules` - Categorized instructions and guidelines  
- **Continue** - `.continue/config.json` - System messages and configuration

### ⏳ Planned
- **Claude Code** - Context-based prompts
- **Kiro** - AI-powered code assistance
- **Cline** - Terminal-based AI coding
- **Codeium** - Context-based prompts
- **Tabnine** - Team-specific configurations
- **Amazon Q** - Comment-based prompts
- **JetBrains AI** - IDE-integrated prompts

## 🗂️ Example Configurations

See the [`examples/`](./examples/) directory for sample configurations:

- [React TypeScript Project](./examples/basic/react-typescript.apm.yaml)
- [Node.js API Service](./examples/basic/node-api.apm.yaml)

## 🚀 Installation & Quick Start

### Installation

```bash
# Install from source (recommended for now)
git clone https://github.com/flamingquaks/agent-prompt-mapper.git
cd agent-prompt-mapper
pip install -e .
```

### Quick Start

```bash
# 1. Initialize a new project (choose from basic, react, api templates)
apm init --template react --output my-project.apm.yaml

# 2. Validate your configuration
apm validate my-project.apm.yaml

# 3. Generate editor-specific prompts
apm generate my-project.apm.yaml --all

# 4. Your AI editor prompts are ready!
ls .github/copilot-instructions.md
ls .cursorrules  
ls .continue/config.json
```

### Available Commands

- `apm init` - Create a new universal prompt file with templates
- `apm validate` - Check your configuration for errors
- `apm generate` - Create editor-specific prompts
- `apm list-editors` - Show supported editors and their status

For detailed usage instructions, see [`GETTING_STARTED.md`](./GETTING_STARTED.md).

## 🤝 Contributing

This project is actively developing! We welcome:
- Bug reports and feature requests
- Pull requests for additional editor support
- Documentation improvements
- Testing and feedback on the UPF format
- Ideas for advanced features

See the [Implementation Roadmap](./docs/IMPLEMENTATION_ROADMAP.md) for planned features and current progress.

## 📚 Documentation

### Core Documentation
- **[Getting Started Guide](./GETTING_STARTED.md)** - Comprehensive setup and usage guide
- **[Advanced Template Features](./docs/ADVANCED_FEATURES.md)** - Variables, conditionals, and imports
- **[Editor Adapters](./docs/ADAPTERS.md)** - Detailed guide to all supported AI editors
- **[Implementation Roadmap](./docs/IMPLEMENTATION_ROADMAP.md)** - Development progress and plans

### Key Features

#### 🔄 Variable Substitution
Use template variables to create reusable, customizable prompts:

```yaml
metadata:
  title: "{{{ PROJECT_NAME }}} Assistant"
  author: "{{{ AUTHOR_EMAIL }}}"

variables:
  PROJECT_NAME: "MyProject"
  AUTHOR_EMAIL: "team@example.com"
```

Override variables from CLI:
```bash
apm generate --editor claude project.apm.yaml \
  -V PROJECT_NAME="CustomProject" \
  -V AUTHOR_EMAIL="custom@example.com"
```

#### 🎯 Conditional Instructions
Provide editor-specific instructions:

```yaml
conditions:
  - if: "EDITOR == \"claude\""
    then:
      instructions:
        general:
          - "Claude: Provide detailed explanations"
  - if: "EDITOR == \"continue\""
    then:
      instructions:
        general:
          - "Continue: Generate comprehensive completions"
```

#### 📦 Import System
Share common configurations across projects:

```yaml
imports:
  - path: "shared/base-config.apm.yaml"
    prefix: "shared"

# Imported instructions get prefixed: [shared] Follow coding standards
# Imported examples get prefixed: shared_example_name
# Imported variables get prefixed: shared_VARIABLE_NAME
```

#### 🎨 Multiple Editor Support
Generate optimized configurations for all major AI coding assistants:

- **Claude Code** → `.claude/context.md`
- **Continue** → `.continue/config.json` 
- **Cline** → `.cline/config.json` + `cline-context.md`
- **Codeium** → `.codeium/context.json` + `.codeiumrc`
- **GitHub Copilot** → `.github/copilot-instructions.md`
- **Cursor** → `.cursorrules`

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
