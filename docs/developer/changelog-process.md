# Changelog Process

PrompTrek uses [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) to automatically generate and maintain a changelog. This ensures consistent commit messages and provides a clear history of changes for users and contributors.

## Overview

The changelog process is fully automated through GitHub Actions and conventional commits. Every commit following the conventional format contributes to the changelog, and releases are created automatically based on semantic versioning rules.

## Conventional Commit Format

All commits must follow this format:

```
type(scope): description

[optional body]

[optional footer]
```

### Commit Types

| Type | Description | Changelog Section | Version Bump |
|------|-------------|-------------------|--------------|
| `feat` | New feature | Features | Minor (0.x.0) |
| `fix` | Bug fix | Bug Fixes | Patch (0.0.x) |
| `docs` | Documentation | Documentation | None |
| `style` | Code style (formatting, etc.) | Not in changelog | None |
| `refactor` | Code refactoring | Not in changelog | None |
| `test` | Tests | Not in changelog | None |
| `chore` | Maintenance | Not in changelog | None |
| `ci` | CI/CD changes | Not in changelog | None |
| `build` | Build system | Not in changelog | None |
| `perf` | Performance | Performance | Patch (0.0.x) |
| `revert` | Revert commit | Reverts | Patch (0.0.x) |

### Scopes

Scopes help organize changes by component:

- **`cli`**: Command-line interface components
- **`core`**: Core functionality (models, parser, validator)
- **`adapters`**: Editor adapters
- **`templates`**: Template system and files
- **`docs`**: Documentation
- **`parser`**: YAML/UPF parsing functionality
- **`validator`**: Validation logic
- **`utils`**: Utility functions
- **`tests`**: Test files and testing infrastructure
- **`deps`**: Dependencies
- **`changelog`**: Changelog-related changes

### Examples

**Good commit messages:**

```bash
feat(adapters): add support for Windsurf editor
fix(parser): handle empty instructions gracefully
docs(readme): update installation instructions
refactor(core): simplify variable substitution logic
test(cli): add integration tests for generate command
chore(deps): update dependencies to latest versions
ci(changelog): add automated changelog generation
perf(parser): optimize YAML parsing for large files
```

**Poor commit messages:**

```bash
# Too vague
fix: bug fix
update: updated files

# Missing type
update readme

# Wrong format
FIX(parser) - fixed issue with variables

# Not imperative mood
fixed the bug in parser
added new feature to CLI
```

## Breaking Changes

For breaking changes, add `BREAKING CHANGE:` in the footer or use `!` after the type/scope:

### Method 1: Using !

```bash
feat(core)!: remove deprecated API methods

The old generatePrompt method has been removed.
Use the new generate method instead.
```

### Method 2: Using Footer

```bash
feat(core): update schema to v3.0.0

BREAKING CHANGE: Schema v1.0.0 is no longer supported.
Use 'promptrek migrate' to upgrade your configuration files.
```

Breaking changes trigger a **major version bump** (x.0.0).

## Changelog Generation

### Automatic Generation

Changelogs are automatically generated and updated by GitHub Actions:

1. **On Releases**: When a version tag is created
2. **On Pull Requests**: Preview in PR comments
3. **On Main Branch**: Keep CHANGELOG.md up to date

### Manual Generation

For local testing or development:

```bash
# Generate changelog from git history
npm install -g conventional-changelog-cli
conventional-changelog -p angular -i CHANGELOG.md -s -r 0
```

### Configuration

Changelog generation is configured in `.conventional-changelog.json`:

```json
{
  "types": [
    {"type": "feat", "section": "Features"},
    {"type": "fix", "section": "Bug Fixes"},
    {"type": "perf", "section": "Performance Improvements"},
    {"type": "revert", "section": "Reverts"},
    {"type": "docs", "section": "Documentation"},
    {"type": "style", "hidden": true},
    {"type": "refactor", "hidden": true},
    {"type": "test", "hidden": true},
    {"type": "build", "hidden": true},
    {"type": "ci", "hidden": true},
    {"type": "chore", "hidden": true}
  ]
}
```

## Release Process

### Semantic Versioning

PrompTrek follows [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH
```

- **MAJOR** (x.0.0): Breaking changes
- **MINOR** (0.x.0): New features (backward compatible)
- **PATCH** (0.0.x): Bug fixes (backward compatible)

### Automated Release Workflow

1. **Commits accumulate** on main branch following conventional format

2. **Version is determined** based on commits since last release:
   - `feat` → Minor bump
   - `fix` or `perf` → Patch bump
   - `BREAKING CHANGE` → Major bump

3. **Tag is created** (manually or automatically)

4. **GitHub Actions triggers**:
   - Generate changelog from commits
   - Update CHANGELOG.md
   - Create GitHub release with notes
   - Build and publish to PyPI
   - Update documentation

### Creating a Release

Maintainers create releases:

1. **Ensure all changes are merged** to main branch

2. **Determine version number** based on changes:
   ```bash
   # Review unreleased changes
   git log $(git describe --tags --abbrev=0)..HEAD --oneline

   # Check for breaking changes
   git log $(git describe --tags --abbrev=0)..HEAD --grep="BREAKING CHANGE"
   ```

3. **Create and push tag**:
   ```bash
   # For minor release (new features)
   git tag v1.2.0
   git push origin v1.2.0

   # For patch release (bug fixes)
   git tag v1.1.1
   git push origin v1.1.1

   # For major release (breaking changes)
   git tag v2.0.0
   git push origin v2.0.0
   ```

4. **GitHub Actions handles the rest**:
   - Generates changelog
   - Creates GitHub release
   - Publishes to PyPI
   - Updates documentation

## Changelog Format

PrompTrek follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Features
- feat(adapters): add Windsurf editor support (#123)
- feat(cli): add refresh command for dynamic variables (#124)

### Bug Fixes
- fix(parser): handle empty instructions gracefully (#125)
- fix(adapters): correct Claude file paths (#126)

### Documentation
- docs(cli): add migration command documentation (#127)

## [1.2.0] - 2024-01-15

### Features
- feat(adapters): add Continue editor support (#110)
- feat(core): add variable substitution (#111)

### Bug Fixes
- fix(validator): improve error messages (#112)

### BREAKING CHANGES
- feat(core)!: update schema to v3.0.0 (#113)

  Schema v1.0.0 is no longer supported. Use `promptrek migrate` to upgrade.

## [1.1.0] - 2024-01-01

### Features
- feat(cli): add interactive mode (#100)

### Bug Fixes
- fix(cli): improve error handling (#101)
```

## Best Practices

### Writing Good Commit Messages

1. **Be descriptive**: Clearly explain what the change does
   ```bash
   # Good
   feat(adapters): add Windsurf editor with MCP server support

   # Poor
   feat: add support
   ```

2. **Use imperative mood**: "add feature" not "added feature"
   ```bash
   # Good
   fix(parser): handle edge case in YAML parsing

   # Poor
   fixed: handled edge case
   ```

3. **Reference issues**: Include issue numbers when relevant
   ```bash
   feat(cli): add --headless flag for autonomous agents

   Adds support for headless mode in generate command
   to enable autonomous AI agent operation.

   Closes #123
   ```

4. **Keep subject line concise**: Under 50 characters
   ```bash
   # Good (48 chars)
   feat(adapters): add Claude Code editor support

   # Too long (62 chars)
   feat(adapters): add support for Claude Code editor with full features
   ```

5. **Explain the "why" in body**: Not just the "what"
   ```bash
   refactor(core): extract variable substitution to utils

   Variable substitution logic was duplicated across adapters.
   Extracting to utils module improves maintainability and
   reduces code duplication.
   ```

### Examples by Type

#### Features

```bash
feat(adapters): add Cursor IDE adapter

Implements adapter for Cursor IDE .cursorrules file format.
Supports single-file configuration and variable substitution.

Closes #150
```

#### Bug Fixes

```bash
fix(parser): handle malformed YAML gracefully

Previously, the parser would crash on invalid YAML.
Now it provides a helpful error message with line number
and suggests common fixes.

Fixes #175
```

#### Documentation

```bash
docs(contributing): add conventional commit guidelines

Adds detailed explanation of commit message format and
examples to help new contributors understand our
expectations for changelog automation.
```

#### Breaking Changes

```bash
feat(core)!: migrate to v3 schema format

BREAKING CHANGE: v1.0.0 schema is no longer supported.

The new v3 schema uses markdown-first content and top-level
plugin fields. Use `promptrek migrate` to upgrade existing
configuration files.

Migration guide: docs/migration-guide.md

Closes #200
```

## Validation and Enforcement

### Pre-commit Validation

Commit messages are validated by commitlint:

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/commitizen-tools/commitizen
  rev: v3.10.0
  hooks:
    - id: commitizen
      stages: [commit-msg]
```

### CI/CD Validation

GitHub Actions validates commit messages in PRs:

```yaml
# .github/workflows/validate.yml
- name: Validate Commit Messages
  uses: wagoid/commitlint-github-action@v5
  with:
    configFile: .commitlintrc.json
```

### Configuration

Commitlint configuration in `.commitlintrc.json`:

```json
{
  "extends": ["@commitlint/config-conventional"],
  "rules": {
    "type-enum": [
      2,
      "always",
      [
        "feat",
        "fix",
        "docs",
        "style",
        "refactor",
        "test",
        "chore",
        "ci",
        "build",
        "perf",
        "revert"
      ]
    ],
    "scope-enum": [
      2,
      "always",
      [
        "cli",
        "core",
        "adapters",
        "templates",
        "docs",
        "parser",
        "validator",
        "utils",
        "tests",
        "deps",
        "changelog"
      ]
    ]
  }
}
```

## Troubleshooting

### Commit Message Validation Fails

**Problem**: Pre-commit hook rejects your commit message

**Solution**: Ensure message follows format:
```bash
# Check your message
git log -1 --pretty=%B

# Amend if needed
git commit --amend

# Follow the format
type(scope): description
```

### Changelog Not Updating

**Problem**: Changelog doesn't include your changes

**Solution**: Ensure commits are:
1. Properly formatted (conventional commits)
2. Include the right types (feat, fix, perf)
3. Merged to main branch

### Wrong Version Bump

**Problem**: Release gets wrong version number

**Solution**: Check commits for:
1. `BREAKING CHANGE` in footer (triggers major)
2. `feat` type (triggers minor)
3. `fix` or `perf` type (triggers patch)

### Missing Scope or Wrong Scope

**Problem**: Scope validation fails

**Solution**: Use approved scopes from `.commitlintrc.json` or add new scope to configuration.

## Resources

### Internal Documentation

- [Contributing Guide](contributing.md) - General contribution guidelines
- [Project Structure](project-structure.md) - Overall project conventions
- [Architecture](architecture.md) - System architecture

### External Resources

- [Conventional Commits](https://www.conventionalcommits.org/) - Commit specification
- [Keep a Changelog](https://keepachangelog.com/) - Changelog format
- [Semantic Versioning](https://semver.org/) - Versioning specification
- [commitlint](https://commitlint.js.org/) - Commit message linter

## Getting Help

- Check existing commit messages for examples
- Review the Conventional Commits specification
- Ask in [GitHub Discussions](https://github.com/flamingquaks/promptrek/discussions)
- Open an issue if you find problems with the automation

Thank you for helping maintain PrompTrek's clear and consistent changelog!
