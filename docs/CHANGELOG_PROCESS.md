# Changelog Process

This document describes how PrompTrek uses conventional commits to automatically generate changelogs.

## Overview

PrompTrek uses [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification to automatically generate and maintain a changelog. This ensures consistent commit messages and provides a clear history of changes for users and contributors.

## Conventional Commit Format

All commits should follow this format:

```
type(scope): description

[optional body]

[optional footer]
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools and libraries
- **ci**: Changes to CI configuration files and scripts
- **build**: Changes that affect the build system or external dependencies
- **perf**: A code change that improves performance
- **revert**: Reverts a previous commit

### Scopes

- **cli**: Command-line interface components
- **core**: Core functionality (models, parser, validator)
- **adapters**: Editor adapters
- **templates**: Template system and files
- **docs**: Documentation
- **parser**: YAML/UPF parsing functionality
- **validator**: Validation logic
- **utils**: Utility functions
- **tests**: Test files and testing infrastructure
- **deps**: Dependencies
- **changelog**: Changelog-related changes

### Examples

```bash
feat(adapters): add support for new Windsurf editor
fix(parser): handle empty instructions gracefully
docs(readme): update installation instructions
refactor(core): simplify variable substitution logic
test(cli): add integration tests for generate command
chore(deps): update dependencies to latest versions
ci(changelog): add automated changelog generation
```

## Breaking Changes

For breaking changes, add `BREAKING CHANGE:` in the footer or use `!` after the type:

```
feat(core)!: remove deprecated API methods

BREAKING CHANGE: The old `generatePrompt` method has been removed. Use `generate` instead.
```

## Automation

### Continuous Integration

The CI pipeline automatically validates commit messages using [commitlint](https://commitlint.js.org/):

- **File**: `.github/workflows/ci.yml`
- **Config**: `.commitlintrc.json`
- **Trigger**: On pull requests to main/develop branches

### Changelog Generation

Changelogs are automatically generated and updated:

1. **On Releases**: The release workflow generates changelog entries
2. **On Main Branch**: Push to main branch updates the changelog
3. **Manual**: Use `scripts/generate-changelog.sh` for local testing

### Configuration Files

- **`.commitlintrc.json`**: Commitlint configuration
- **`.conventional-changelog.json`**: Changelog generation settings
- **`CHANGELOG.md`**: The main changelog file

## Local Development

### Validating Commits

Before committing, you can validate your commit message:

```bash
# Install commitlint (if not already installed)
npm install -g @commitlint/cli @commitlint/config-conventional

# Validate last commit
npx commitlint --from HEAD~1 --to HEAD --verbose
```

### Generating Changelog Locally

```bash
# Generate changelog from git history
./scripts/generate-changelog.sh

# Or manually with conventional-changelog
npm install -g conventional-changelog-cli
conventional-changelog -p angular -i CHANGELOG.md -s -r 0
```

## Release Process

The automated release process:

1. **Tag Creation**: Create a version tag (e.g., `v1.0.0`)
2. **Changelog Update**: Automatically generate changelog entries
3. **GitHub Release**: Create release with changelog content
4. **PyPI Publish**: Publish package to PyPI

## Best Practices

### Writing Good Commit Messages

1. **Be descriptive**: Clearly explain what the change does
2. **Use imperative mood**: "add feature" not "added feature"
3. **Reference issues**: Include issue numbers when relevant
4. **Keep it concise**: Subject line should be under 50 characters
5. **Add body when needed**: Explain the "why" in the body

### Examples of Good Commits

```bash
feat(cli): add --output-dir option to generate command

Allows users to specify a custom output directory for generated files.
This addresses the need for better control over file placement.

Closes #123

fix(parser): handle malformed YAML files gracefully

Previously, the parser would crash on invalid YAML. Now it provides
a helpful error message and suggests fixes.

docs(contributing): add conventional commit guidelines

Helps new contributors understand our commit message format and
expectations for changelog automation.
```

### Examples of Poor Commits

```bash
# Too vague
fix: bug fix

# Missing type
update readme

# Wrong format
FIX(parser) - fixed issue with variables

# Not imperative mood
fixed the bug in parser
added new feature to CLI
```

## Troubleshooting

### Common Issues

1. **Commit validation fails**: Check that your commit message follows the conventional format
2. **Changelog not updating**: Ensure commits are properly formatted and include the right types
3. **Missing scope**: Add appropriate scope from the approved list

### Getting Help

- Check existing commit messages for examples
- Review the [Conventional Commits specification](https://www.conventionalcommits.org/)
- Ask in discussions or issues for guidance

## Related Documentation

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md): Overall project conventions
- [CONTRIBUTING.md](../.github/CONTRIBUTING.md): General contribution guidelines
- [Keep a Changelog](https://keepachangelog.com/): Changelog format specification