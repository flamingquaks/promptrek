# Examples

Welcome to the PrompTrek examples gallery! This section provides comprehensive, real-world examples to help you get the most out of PrompTrek.

## Quick Navigation

### Basic Examples

Perfect for getting started with PrompTrek in common project types:

- **[React TypeScript](basic/react-typescript.md)** - Modern React application with TypeScript
- **[Node.js API](basic/node-api.md)** - RESTful API service with Express and TypeScript

### Advanced Examples

Complex project architectures and specialized use cases:

- **[NX Monorepo](advanced/monorepo.md)** - Large-scale monorepo with multiple apps and shared libraries

### Plugin Examples

Learn how to leverage PrompTrek's plugin ecosystem:

- **[MCP Servers](plugins/mcp-servers.md)** - Model Context Protocol server integration
- **[Custom Commands](plugins/custom-commands.md)** - Slash commands for AI editors

## Example Structure

Each example includes:

- **Complete YAML configuration** - Full `.promptrek.yaml` file you can use as a template
- **Detailed explanations** - What each section does and why
- **Best practices** - Recommended patterns and conventions
- **Usage instructions** - How to generate and use the configurations
- **Editor-specific notes** - Tips for different AI editors

## How to Use Examples

### 1. Browse the Examples

Navigate through the examples to find one that matches your project type or use case.

### 2. Copy and Customize

Copy the YAML configuration and adapt it to your project:

```bash
# Download example
curl -o my-project.promptrek.yaml https://raw.githubusercontent.com/flamingquaks/promptrek/main/examples/basic/react-typescript.promptrek.yaml

# Edit to match your project
vim my-project.promptrek.yaml
```

### 3. Validate

Ensure your configuration is valid:

```bash
promptrek validate my-project.promptrek.yaml
```

### 4. Generate

Create editor-specific configurations:

```bash
# Generate for specific editor
promptrek generate my-project.promptrek.yaml --editor cursor

# Generate for all configured editors
promptrek generate my-project.promptrek.yaml --all
```

## Available Examples by Technology

### Frontend

- **React TypeScript** - Component-based UI development
- **NX Monorepo (Web Apps)** - Shared UI libraries

### Backend

- **Node.js API** - REST API with Express
- **NX Monorepo (NestJS)** - Backend services

### Full-Stack

- **NX Monorepo** - Complete frontend + backend setup

### DevOps & Plugins

- **MCP Servers** - External tool integration
- **Custom Commands** - Workflow automation

## Example Templates

### Minimal Example

```yaml
# yaml-language-server: $schema=https://promptrek.ai/schema/v3.1.0.json
schema_version: "3.1.0"
metadata:
  title: "My Project"
  description: "AI assistant configuration"

content: |
  # Project Guidelines

  - Write clean, maintainable code
  - Follow project conventions
  - Add tests for new features

variables:
  PROJECT_NAME: "my-project"
```

### With Plugins

```yaml
# yaml-language-server: $schema=https://promptrek.ai/schema/v3.1.0.json
schema_version: "3.1.0"
metadata:
  title: "Full-Featured Project"

content: |
  # Development Guidelines
  - Follow coding standards
  - Write comprehensive tests

# MCP Server integration
mcp_servers:
  - name: github
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"

# Custom commands
commands:
  - name: review
    description: "Code review"
    prompt: "Review this code for quality and best practices"

variables:
  GITHUB_TOKEN: "ghp_your_token"
```

### Multi-Document Example

```yaml
# yaml-language-server: $schema=https://promptrek.ai/schema/v3.1.0.json
schema_version: "3.1.0"
metadata:
  title: "Multi-Document Project"

content: |
  # General Guidelines
  - Maintain code quality
  - Document thoroughly

# Document for TypeScript files
documents:
  - name: typescript
    content: |
      # TypeScript Guidelines
      - Use strict mode
      - Prefer interfaces over types
    file_globs: "**/*.{ts,tsx}"
    always_apply: false

  - name: testing
    content: |
      # Testing Standards
      - Write unit tests for all functions
      - Aim for 80%+ coverage
    file_globs: "**/*.{test,spec}.{ts,tsx,js}"
```

## Learning Path

### Beginner

1. Start with **[React TypeScript](basic/react-typescript.md)** or **[Node.js API](basic/node-api.md)**
2. Learn the basic YAML structure
3. Understand metadata and content sections
4. Practice variable substitution

### Intermediate

1. Explore **[Custom Commands](plugins/custom-commands.md)**
2. Add multi-document support for different file types
3. Use path-specific rules (Copilot, Cursor)
4. Implement validation schemas

### Advanced

1. Study **[NX Monorepo](advanced/monorepo.md)**
2. Configure **[MCP Servers](plugins/mcp-servers.md)**
3. Set up autonomous agents
4. Implement event hooks
5. Create custom workflows

## Tips and Best Practices

### Organization

!!! tip "Keep it Organized"
    - Use clear section headings in your content
    - Group related guidelines together
    - Separate concerns (style, testing, security)

### Variables

!!! tip "Use Variables Wisely"
    - Define all environment-specific values as variables
    - Use `{{{ }}}` syntax for substitution
    - Override variables per environment using `-V` flag

### Documentation

!!! tip "Document Everything"
    - Explain why rules exist, not just what they are
    - Include code examples for complex patterns
    - Link to external documentation when relevant

### Testing

!!! tip "Validate Early"
    - Use `promptrek validate` before committing
    - Test generated files in actual editors
    - Set up pre-commit hooks for automatic validation

## Community Examples

Want to share your example? We welcome contributions!

1. Create a `.promptrek.yaml` file for your use case
2. Add comprehensive comments and documentation
3. Test with multiple editors
4. Submit a pull request to the `examples/` directory

See our [Contributing Guide](../community/contributing.md) for details.

## Additional Resources

- **[User Guide](../user-guide/index.md)** - Complete PrompTrek documentation
- **[CLI Reference](../cli/index.md)** - Command-line interface documentation
- **[Schema Reference](../reference/glossary.md)** - Configuration schema details
- **[GitHub Repository](https://github.com/flamingquaks/promptrek)** - Source code and more examples

## Need Help?

- Check the **[FAQ](../reference/faq.md)** for common questions
- Visit **[Troubleshooting](../reference/troubleshooting.md)** for solutions to common issues
- Join the discussion on [GitHub Discussions](https://github.com/flamingquaks/promptrek/discussions)
- Report bugs via [GitHub Issues](https://github.com/flamingquaks/promptrek/issues)

---

Happy coding with PrompTrek! Remember, the best AI assistant is one that's configured to understand your project's unique needs.
