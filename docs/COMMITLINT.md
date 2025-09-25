# Commitlint Configuration

This project uses [commitlint](https://commitlint.js.org/) to ensure consistent commit message format following the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Workflow Strategy

**Important:** Commitlint is configured to validate **only PR squashed merge commits**, not individual development commits. This allows:

- ✅ Developers can use any commit message format during feature branch development
- ✅ Only the final squashed commit message needs to follow conventional commit format
- ✅ Reduces friction during development while ensuring clean main branch history
- ✅ Enables automated changelog generation from main branch commits

## Configuration

The commitlint configuration is defined in `.commitlintrc.json` at the project root.

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

### Optional Scopes

Scopes are optional but encouraged for better organization:

- `cli`: Command-line interface changes
- `core`: Core functionality changes
- `adapters`: AI editor adapter changes
- `templates`: Template changes
- `docs`: Documentation changes
- `parser`: Parser-related changes
- `validator`: Validation logic changes
- `utils`: Utility function changes
- `tests`: Test-related changes
- `deps`: Dependency updates
- `changelog`: Changelog updates
- `config`: Configuration changes
- `scripts`: Script changes
- `workflows`: GitHub Actions workflow changes

### Rules

- **Subject**: Must not be empty, no period at the end, not start/pascal/upper case
- **Type**: Must be lowercase and from the allowed list above
- **Scope**: Optional, must be lowercase if provided
- **Format**: `type(scope): description` or `type: description`

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

### CI/CD Integration for PR Squash Commits

For the recommended workflow of validating only squashed merge commits, configure commitlint to run after PRs are merged:

**GitHub Actions Example:**
```yaml
name: Validate Squashed Commit Messages
on:
  push:
    branches: [main, master]

jobs:
  validate-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          # Fetch enough history to get the previous commit for comparison
          fetch-depth: 2
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm install @commitlint/cli @commitlint/config-conventional
      - name: Validate squashed commit message
        run: |
          # Validate only the latest commit (the squashed merge commit)
          git log -1 --pretty=format:"%s" | npx commitlint
```

**Alternative: Validate PR Title (Preview)**
If you want to validate the expected commit message before merging:
```yaml
name: Validate PR Title Format
on:
  pull_request:
    types: [opened, edited, synchronize]

jobs:
  validate-pr-title:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm install @commitlint/cli @commitlint/config-conventional
      - name: Validate PR title (future commit message)
        run: echo "${{ github.event.pull_request.title }}" | npx commitlint
```

### Local Git Hooks (Optional)

If you want to validate commits locally during development, you can set up git hooks:

```bash
# Install husky
npm install husky --save-dev

# Add commit-msg hook
npx husky add .husky/commit-msg 'npx commitlint --edit "$1"'
```

**Note:** Local hooks are optional since the main validation happens on PR squash commits.

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
