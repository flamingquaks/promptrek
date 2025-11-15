# Your First PrompTrek Project

This step-by-step tutorial will guide you through creating your first PrompTrek configuration from scratch.

## What We'll Build

We'll create a configuration for a React TypeScript project that:

- Provides clear coding guidelines to AI assistants
- Uses variables for reusability
- Includes path-specific instructions for different file types
- Works across multiple AI editors

## Prerequisites

Make sure you have PrompTrek installed:

```bash
promptrek --version
```

If not, see the [Installation Guide](installation.md).

## Step 1: Create the Project Directory

```bash
mkdir my-react-app
cd my-react-app
git init
```

## Step 2: Initialize PrompTrek

Use the React template to get started:

```bash
promptrek init --template react --output .promptrek.yaml --setup-hooks
```

This command:
- ✅ Creates `.promptrek.yaml` with React-specific guidelines
- ✅ Sets up `.gitignore` to exclude generated files
- ✅ Configures pre-commit hooks for validation

## Step 3: Examine the Generated Configuration

Open `.promptrek.yaml` and you'll see:

```yaml
schema_version: "3.1.0"

metadata:
  title: "React TypeScript Project Assistant"
  description: "AI coding assistant for React with TypeScript"
  version: "1.0.0"
  author: "Your Name <your.email@example.com>"
  tags: [react, typescript, frontend, web]

content: |
  # React TypeScript Project

  ## Project Overview
  Modern React application with TypeScript, following best practices.

  ## Development Guidelines

  ### General Principles
  - Use functional components with hooks
  - Follow React best practices
  - Write type-safe TypeScript code
  - Maintain comprehensive test coverage

  ### Code Style
  - Use meaningful component and variable names
  - Keep components small and focused
  - Prefer composition over inheritance
  - Use TypeScript strict mode

variables:
  PROJECT_NAME: "my-react-app"
  FRAMEWORK: "React 18"
  LANGUAGE: "TypeScript 5"
```

## Step 4: Customize Your Configuration

Edit `.promptrek.yaml` to match your project:

```yaml
schema_version: "3.1.0"

metadata:
  title: "{{{ PROJECT_NAME }}} Assistant"
  description: "AI assistant for {{{ PROJECT_NAME }}}"
  version: "1.0.0"
  author: "Your Name <your.email@example.com>"
  tags: [react, typescript, vite, tailwind]

content: |
  # {{{ PROJECT_NAME }}}

  ## Technology Stack
  - **Framework**: {{{ FRAMEWORK }}}
  - **Language**: {{{ LANGUAGE }}}
  - **Build Tool**: {{{ BUILD_TOOL }}}
  - **Styling**: {{{ CSS_FRAMEWORK }}}

  ## Development Guidelines

  ### Component Structure
  ```tsx
  // Use this pattern for all components
  import { FC } from 'react';

  interface Props {
    title: string;
  }

  export const MyComponent: FC<Props> = ({ title }) => {
    return <div>{title}</div>;
  };
  ```

  ### State Management
  - Use useState for local state
  - Use useContext for global state
  - Consider Zustand for complex state

  ### Styling
  - Use Tailwind CSS utility classes
  - Follow mobile-first approach
  - Ensure dark mode compatibility

variables:
  PROJECT_NAME: "my-react-app"
  FRAMEWORK: "React 18"
  LANGUAGE: "TypeScript 5"
  BUILD_TOOL: "Vite"
  CSS_FRAMEWORK: "Tailwind CSS"

documents:
  - name: "components"
    content: |
      # React Component Guidelines

      - Create one component per file
      - Use PascalCase for component names
      - Export named exports, not default
      - Include TypeScript interfaces for props
    file_globs: "src/components/**/*.{tsx,ts}"

  - name: "tests"
    content: |
      # Testing Guidelines

      - Use React Testing Library
      - Test user interactions, not implementation
      - Aim for 80% code coverage
      - Mock external dependencies
    file_globs: "**/*.test.{ts,tsx}"

  - name: "hooks"
    content: |
      # Custom Hooks Guidelines

      - Prefix hook names with 'use'
      - Keep hooks focused and reusable
      - Document hook parameters and return values
    file_globs: "src/hooks/**/*.{ts,tsx}"
```

## Step 5: Validate Your Configuration

Check that your configuration is valid:

```bash
promptrek validate .promptrek.yaml --strict
```

Expected output:
```
✓ Configuration is valid!
  Schema: v3.1.0
  Metadata: ✓
  Variables: 5 defined
  Documents: 3 documents
```

## Step 6: Generate Editor Configurations

Generate configurations for all your team's editors:

```bash
promptrek generate .promptrek.yaml --all
```

This creates:
- `.github/copilot-instructions.md` - For GitHub Copilot users
- `.cursor/rules/` - For Cursor users
- `.continue/rules/` - For Continue users
- `.claude/CLAUDE.md` - For Claude Code users
- And more...

## Step 7: Test with Your Editor

### For GitHub Copilot Users

1. Open the project in VSCode with GitHub Copilot installed
2. Create a new file: `src/components/Welcome.tsx`
3. Start typing a component and watch Copilot suggest code following your guidelines

### For Cursor Users

1. Open the project in Cursor
2. The rules are automatically loaded from `.cursor/rules/`
3. Ask Cursor to "create a new React component" and see it follow your guidelines

### For Claude Code Users

1. Open the project in a Claude Code-compatible environment
2. The guidelines from `.claude/CLAUDE.md` are automatically used
3. Ask Claude to help with your code

## Step 8: Add Plugin Configuration

Enhance your setup with MCP servers and custom commands:

```yaml
# Add to your .promptrek.yaml

mcp_servers:
  - name: filesystem
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "./src"]
    description: "File system access for src directory"

commands:
  - name: add-component
    description: "Create a new React component with boilerplate"
    prompt: |
      Create a new React component with:
      - TypeScript interface for props
      - Functional component with FC type
      - Proper imports and exports
      - Basic Tailwind styling

agents:
  - name: test-writer
    description: "Write tests for React components"
    prompt: |
      Write comprehensive tests using React Testing Library:
      - Test component rendering
      - Test user interactions
      - Test edge cases
      - Mock external dependencies
```

## Step 9: Set Up Version Control

Your `.gitignore` is already configured, so just commit:

```bash
git add .promptrek.yaml .gitignore .pre-commit-config.yaml
git commit -m "feat: add PrompTrek configuration"
```

The generated files (`.cursor/`, `.github/copilot-instructions.md`, etc.) are automatically ignored.

## Step 10: Share with Your Team

Team members can now:

```bash
git clone <your-repo>
cd <your-repo>
promptrek generate .promptrek.yaml --all
```

Each team member gets configurations for their preferred editor!

## Next Steps

### Learn More

- [Variable Substitution](../user-guide/advanced/variables.md) - Advanced variable usage
- [Multi-Document Support](../user-guide/advanced/multi-document.md) - Path-specific instructions
- [Plugin Configuration](../user-guide/plugins/index.md) - MCP servers, commands, agents
- [Pre-commit Integration](../user-guide/workflows/pre-commit.md) - Automated validation

### Explore Examples

- [Advanced React Native Example](../examples/advanced/react-native.md)
- [Full-Stack Next.js Example](../examples/advanced/nextjs.md)
- [NX Monorepo Example](../examples/advanced/monorepo.md)

### Get Help

- [FAQ](../reference/faq.md) - Common questions
- [Troubleshooting](../reference/troubleshooting.md) - Common issues
- [GitHub Issues](https://github.com/flamingquaks/promptrek/issues) - Report bugs or request features
