# Contributing to PrompTrek VSCode Extension

Thank you for your interest in contributing to the PrompTrek VSCode extension! This document provides guidelines for contributing to the extension.

## Development Setup

1. **Prerequisites:**
   - Node.js 18.x or higher
   - Visual Studio Code 1.85.0 or higher
   - PrompTrek CLI installed

2. **Clone and Install:**
   ```bash
   cd promptrek/vscode-extension
   npm install
   ```

3. **Development Workflow:**
   ```bash
   # Compile TypeScript
   npm run compile

   # Watch mode (auto-compile on changes)
   npm run watch

   # Lint code
   npm run lint
   ```

4. **Testing:**
   - Press `F5` in VSCode to launch Extension Development Host
   - Test your changes in the development host
   - Check the Debug Console for errors

## Project Structure

```
vscode-extension/
├── src/
│   ├── extension.ts           # Main entry point
│   ├── commands/              # Command implementations
│   │   ├── init.ts           # Initialize configuration
│   │   ├── generate.ts       # Generate editor files
│   │   ├── validate.ts       # Validate configuration
│   │   ├── preview.ts        # Preview output
│   │   └── sync.ts          # Sync from editor files
│   ├── views/                # Tree view providers
│   │   ├── configExplorer.ts # Configuration tree view
│   │   └── editorStatusView.ts # Editor status view
│   ├── utils/                # Utility modules
│   │   ├── promptrekCli.ts   # CLI wrapper
│   │   └── yamlParser.ts     # YAML parsing
│   └── types/                # TypeScript types
│       └── promptrek.ts      # Type definitions
├── media/                    # Icons and images
├── package.json             # Extension manifest
└── tsconfig.json           # TypeScript configuration
```

## Code Style

- Use TypeScript strict mode
- Follow existing code formatting
- Use meaningful variable and function names
- Add JSDoc comments for public APIs
- Keep functions focused and small

## Adding New Features

### 1. New Command

1. Create a new file in `src/commands/`
2. Implement the command logic
3. Register the command in `src/extension.ts`
4. Add command to `package.json` contributions
5. Update README with usage instructions

Example:
```typescript
// src/commands/myCommand.ts
import * as vscode from 'vscode';
import { PrompTrekCli } from '../utils/promptrekCli';

export async function myCommand(cli: PrompTrekCli): Promise<void> {
  // Implementation
}
```

### 2. New Tree View Item

1. Modify the appropriate provider in `src/views/`
2. Add new context value
3. Update `getChildren()` method
4. Add icons and styling
5. Test thoroughly

### 3. New Configuration Setting

1. Add setting to `package.json` contributions
2. Update `src/extension.ts` to use the setting
3. Document in README
4. Provide sensible defaults

## Testing Guidelines

1. **Manual Testing:**
   - Test all commands in the Command Palette
   - Test context menus
   - Test tree view interactions
   - Test with various configuration files
   - Test error handling

2. **Edge Cases:**
   - No configuration file
   - Invalid configuration
   - Missing PrompTrek CLI
   - Network/permission errors

3. **User Experience:**
   - Clear error messages
   - Progress indicators for long operations
   - Confirmation prompts for destructive actions
   - Helpful tooltips and descriptions

## Pull Request Process

1. **Before Submitting:**
   - Test your changes thoroughly
   - Run `npm run lint` and fix any issues
   - Update documentation if needed
   - Add entry to CHANGELOG.md

2. **PR Description:**
   - Describe what changes you made
   - Explain why the changes are needed
   - Include screenshots for UI changes
   - Reference any related issues

3. **Review Process:**
   - Maintainers will review your PR
   - Address any feedback
   - Once approved, your PR will be merged

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(commands): add migrate schema command
fix(views): correct tree view refresh logic
docs(readme): update installation instructions
```

## Issues and Bugs

When reporting issues:
1. Use the GitHub issue tracker
2. Provide a clear description
3. Include steps to reproduce
4. Add screenshots if applicable
5. Specify VSCode and PrompTrek versions

## Feature Requests

We welcome feature requests! Please:
1. Check existing issues first
2. Describe the use case
3. Explain the expected behavior
4. Consider implementation complexity

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

## Questions?

- Check the [main PrompTrek documentation](https://flamingquaks.github.io/promptrek)
- Open a discussion on GitHub
- Review existing issues and PRs

Thank you for contributing to PrompTrek!
