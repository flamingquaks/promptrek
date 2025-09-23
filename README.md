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

This project is currently in the **planning phase**. We are:
- ✅ Researching different AI editors and their prompt formats
- ✅ Designing the universal prompt format specification  
- ✅ Creating the system architecture
- ⏳ Planning the implementation roadmap
- ⏳ Building the CLI tool and core functionality

## 📖 Documentation

All planning documents are available in the [`docs/`](./docs/) directory:

- [Project Planning](./docs/PLANNING.md) - Overall project goals and requirements
- [Editor Research](./docs/EDITOR_RESEARCH.md) - Research on different AI editors
- [System Architecture](./docs/ARCHITECTURE.md) - Technical architecture and design
- [Universal Prompt Format](./docs/UPF_SPECIFICATION.md) - Complete format specification
- [Implementation Roadmap](./docs/IMPLEMENTATION_ROADMAP.md) - Development timeline and phases
- [Project Structure](./docs/PROJECT_STRUCTURE.md) - Repository organization and conventions

## 🎨 Supported Editors (Planned)

- **GitHub Copilot** - `.github/copilot-instructions.md`
- **Cursor** - `.cursorrules`
- **Continue** - `.continue/config.json`
- **Codeium** - Context-based prompts
- **Tabnine** - Team-specific configurations
- **Amazon Q** - Comment-based prompts
- **JetBrains AI** - IDE-integrated prompts

## 🗂️ Example Configurations

See the [`examples/`](./examples/) directory for sample configurations:

- [React TypeScript Project](./examples/basic/react-typescript.apm.yaml)
- [Node.js API Service](./examples/basic/node-api.apm.yaml)

## 🤝 Contributing

This project is in early planning stages. We welcome:
- Feedback on the approach and architecture
- Research on additional AI editors
- Suggestions for the universal prompt format
- Ideas for CLI tool features

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
