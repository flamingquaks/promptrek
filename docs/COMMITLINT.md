# Commitlint Configuration

This project uses [commitlint](https://commitlint.js.org/) to ensure consistent commit message format following the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Configuration

The commitlint configuration is defined in `commitlint.config.js` at the project root.

### Allowed Commit Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (formatting, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `build`: Changes that affect the build system or external dependencies
- `ci`: Changes to our CI configuration files and scripts
- `chore`: Other changes that don't modify src or test files
- `revert`: Reverts a previous commit

### Rules

- **Header length**: Maximum 72 characters
- **Subject**: Must be lowercase, minimum 3 characters, no period at the end
- **Type**: Must be lowercase and from the allowed list above
- **Body/Footer**: Maximum 100 characters per line, blank line required before body/footer

## Usage

### Installation

Since this is a Python project, you'll need Node.js and npm installed to use commitlint:

```bash
# Install commitlint globally
npm install -g @commitlint/cli @commitlint/config-conventional

# Or install locally for the project
npm install @commitlint/cli @commitlint/config-conventional
```

### Manual Validation

To check a commit message manually:

```bash
echo "feat: add new feature" | npx commitlint
```

### Git Hooks Integration

To automatically validate commit messages, install commitlint as a git hook using husky:

```bash
# Install husky
npm install husky --save-dev

# Add commit-msg hook
npx husky add .husky/commit-msg 'npx commitlint --edit "$1"'
```

## Examples

### ✅ Valid Commit Messages

```
feat: add user authentication system
fix: resolve memory leak in parser
docs: update installation instructions
style: format code with black
refactor: extract validation logic to separate module
test: add unit tests for adapter registry
ci: update github actions workflow
chore: update dependencies
```

### ❌ Invalid Commit Messages

```
Add new feature                    # Missing type
feat: Add new feature             # Subject should be lowercase
FEAT: add new feature             # Type should be lowercase
feat:add new feature              # Missing space after colon
feat: add new feature.            # Subject should not end with period
invalid: add new feature          # Invalid type
feat:                             # Subject is empty
```

## Integration with Python Tools

While commitlint requires Node.js, it integrates well with Python development workflows:

- Works alongside Python formatting tools (black, isort)
- Compatible with Python testing frameworks (pytest)
- Follows the same conventional commit format used by many Python projects
- Can be integrated into CI/CD pipelines alongside Python linting tools (flake8, mypy)

## Troubleshooting

If you encounter issues:

1. Ensure Node.js and npm are installed
2. Verify the commitlint configuration file exists and is valid JavaScript
3. Check that the commit message follows the expected format: `type: description`
4. Ensure the type is one of the allowed types listed above
