# Contributing to PrompTrek

Thank you for your interest in contributing to PrompTrek! This guide will help you get started with contributing to the project.

## Quick Start for Contributors

### Prerequisites

- **Python 3.9 or higher** (3.11 recommended)
- **Git** for version control
- **uv** (recommended) or pip for package management
- **A GitHub account**

### Development Setup

1. **Fork the repository** on GitHub

2. **Clone your fork locally:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/promptrek.git
   cd promptrek
   ```

3. **Install development dependencies:**
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

5. **Run tests to verify setup:**
   ```bash
   # Using uv
   uv run pytest

   # Or using pytest directly
   pytest
   ```

## Ways to Contribute

### Bug Reports

Found a bug? Help us fix it!

1. **Search existing issues** to avoid duplicates
2. **Create a new issue** using our bug report template
3. **Include detailed information:**
   - PrompTrek version (`promptrek --version`)
   - Python version (`python --version`)
   - Operating system
   - Steps to reproduce
   - Expected vs actual behavior
   - Any error messages or stack traces

[Report a Bug →](https://github.com/flamingquaks/promptrek/issues/new?template=bug_report.yml)

### Feature Requests

Have an idea for a new feature?

1. **Search existing issues** for similar requests
2. **Create a feature request** using our template
3. **Describe the use case** and expected benefits
4. **Consider implementation** if you plan to work on it

[Request a Feature →](https://github.com/flamingquaks/promptrek/issues/new?template=feature_request.yml)

### Code Contributions

Ready to write some code? Here's how:

#### 1. Choose an Issue

- Look for issues labeled `good first issue` for beginners
- Check issues labeled `help wanted` for areas needing assistance
- Comment on the issue to express interest and get assigned

#### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

**Branch naming**:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test improvements

#### 3. Make Your Changes

Follow our [coding standards](#coding-standards) and write clean, maintainable code.

**Key principles**:
- Write clear, self-documenting code
- Add type hints to all function signatures
- Include docstrings for public APIs
- Follow existing patterns and conventions
- Keep changes focused and atomic

#### 4. Write Tests

All code changes should include appropriate tests:

```bash
# Create test file if needed
touch tests/unit/test_my_feature.py

# Write tests
# Run tests
pytest tests/unit/test_my_feature.py

# Check coverage
pytest --cov=promptrek --cov-report=html
```

**Testing guidelines**:
- Unit tests for individual functions/classes
- Integration tests for complete workflows
- Aim for >90% coverage for new code
- Test both success and failure cases
- Use fixtures for reusable test data

#### 5. Update Documentation

If your changes affect user-facing functionality:

- Update relevant documentation in `docs/`
- Add examples and use cases
- Update command-line help text
- Consider adding to CHANGELOG.md

#### 6. Run Quality Checks

Before committing, ensure code meets quality standards:

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/ --max-line-length=88

# Type checking
mypy src/

# Run all tests
pytest --cov=promptrek
```

Pre-commit hooks will run these automatically on commit.

#### 7. Commit Your Changes

We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: type(scope): description
git commit -m "feat(adapters): add support for new editor"
git commit -m "fix(parser): handle edge case in YAML parsing"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(cli): add integration tests for generate command"
```

**Commit types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `build`: Build system changes
- `perf`: Performance improvements
- `revert`: Revert previous commits

**Commit scopes:**
- `cli`: CLI components
- `core`: Core functionality
- `adapters`: Editor adapters
- `docs`: Documentation
- `tests`: Tests
- `deps`: Dependencies
- `changelog`: Changelog

**Examples:**
```bash
feat(adapters): add Windsurf editor support
fix(parser): handle empty instructions gracefully
docs(cli): improve generate command documentation
test(adapters): add Claude adapter integration tests
refactor(core): simplify variable substitution logic
chore(deps): update dependencies to latest versions
ci(changelog): add automated changelog generation
```

**Breaking changes:**
```bash
# Use ! after type or add BREAKING CHANGE: in footer
feat(core)!: remove deprecated API methods

# Or in commit body
feat(core): update schema to v3.0.0

BREAKING CHANGE: Schema v1.0.0 is no longer supported. Use promptrek migrate to upgrade.
```

#### 8. Push and Create Pull Request

```bash
# Push to your fork
git push origin your-branch-name
```

Then create a pull request on GitHub using our PR template.

**PR guidelines:**
- Clear title describing the change
- Description of what changed and why
- Link to related issues (Fixes #123, Closes #456)
- Screenshots for UI changes
- Testing instructions
- Breaking changes noted clearly

### Documentation

Documentation improvements are always welcome!

- **Fix typos or unclear explanations**
- **Add examples and use cases**
- **Improve API documentation**
- **Create tutorials or guides**
- **Update this website**

Documentation is written in Markdown and built with MkDocs.

### New Editor Support

Want to add support for a new AI editor?

1. **Research the editor's prompt format**
   - File locations
   - Format specifications
   - Plugin/extension system

2. **Create an issue** to discuss the implementation
   - Share editor documentation
   - Discuss approach and file formats

3. **Follow our adapter pattern**
   - See `src/promptrek/adapters/` for examples
   - Extend `EditorAdapter` base class
   - Implement required methods

4. **Add comprehensive tests**
   - Unit tests for adapter logic
   - Integration tests for file generation
   - Test fixtures with examples

5. **Update documentation**
   - Add adapter to `docs/user-guide/adapters/`
   - Update capability matrix
   - Provide usage examples

## Development Guidelines

### Coding Standards

#### Code Quality

- **Type Hints**: All public functions must have type hints
- **Docstrings**: All public classes and functions need docstrings (Google style)
- **Error Handling**: Use proper exception handling with custom exceptions
- **Logging**: Use structured logging throughout the application

#### Code Style

We use automated tools to maintain consistent code style:

```bash
# Format code (Black)
black src/ tests/

# Sort imports (isort)
isort src/ tests/

# Lint code (flake8)
flake8 src/ tests/ --max-line-length=88

# Type checking (mypy)
mypy src/
```

Configuration in `pyproject.toml`:

```toml
[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.9"
strict = true
```

#### Testing Standards

- **Coverage**: Maintain minimum 90% test coverage for new code
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test complete workflows
- **Fixtures**: Use reusable test data and configurations

```bash
# Run tests with coverage
pytest --cov=promptrek --cov-report=html --cov-fail-under=90

# Run specific tests
pytest tests/unit/test_parser.py
pytest -k "test_validate"

# Verbose output
pytest -v
```

### Adding a New Editor Adapter

Complete guide to adding editor support:

1. **Create the adapter class** in `src/promptrek/adapters/`:

```python
# src/promptrek/adapters/myeditor.py
from pathlib import Path
from typing import Union

from .base import EditorAdapter
from ..core.models import UniversalPrompt, UniversalPromptV2, UniversalPromptV3


class MyEditorAdapter(EditorAdapter):
    """Adapter for MyEditor IDE.

    MyEditor stores prompts in .myeditor/config.json format.
    """

    def generate(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: dict[str, str] | None = None,
    ) -> None:
        """Generate MyEditor configuration files.

        Args:
            prompt: Universal prompt configuration
            output_dir: Directory for generated files
            dry_run: If True, show what would be generated
            verbose: Enable verbose output
            variables: Variable substitutions
        """
        # Implementation here
        if dry_run:
            click.echo("Would create: .myeditor/config.json")
            return

        # Create actual files
        config_dir = output_dir / ".myeditor"
        config_dir.mkdir(parents=True, exist_ok=True)

        # Generate configuration
        config = self._build_config(prompt, variables)

        # Write file
        with open(config_dir / "config.json", "w") as f:
            json.dump(config, f, indent=2)

        if verbose:
            click.echo(f"Created .myeditor/config.json")

    def supports_bidirectional_sync(self) -> bool:
        """Whether this adapter supports syncing from editor files."""
        return True  # If you implement parse_files()

    def parse_files(self, source_dir: Path) -> UniversalPromptV3:
        """Parse MyEditor files back to universal format.

        Args:
            source_dir: Directory containing MyEditor files

        Returns:
            Universal prompt in v3 format
        """
        # Implementation for reverse sync
        config_file = source_dir / ".myeditor" / "config.json"

        with open(config_file) as f:
            config = json.load(f)

        # Parse and return UniversalPromptV3
        return UniversalPromptV3(...)
```

2. **Register the adapter** in `src/promptrek/adapters/registry.py`:

```python
from .myeditor import MyEditorAdapter

# In the registry initialization
registry.register("myeditor", MyEditorAdapter, {
    "description": "MyEditor IDE support",
    "capabilities": [AdapterCapability.GENERATES_PROJECT_FILES],
    "file_patterns": [".myeditor/config.json"],
})
```

3. **Add comprehensive tests** in `tests/unit/adapters/test_myeditor.py`:

```python
import pytest
from pathlib import Path
from promptrek.adapters.myeditor import MyEditorAdapter
from promptrek.core.models import UniversalPromptV3, PromptMetadata


@pytest.fixture
def sample_prompt():
    """Sample prompt for testing."""
    return UniversalPromptV3(
        schema_version="3.0.0",
        metadata=PromptMetadata(
            title="Test Project",
            description="Test description",
            version="1.0.0",
        ),
        content="# Test Content",
    )


def test_myeditor_generate(tmp_path, sample_prompt):
    """Test MyEditor file generation."""
    adapter = MyEditorAdapter()

    adapter.generate(
        sample_prompt,
        tmp_path,
        dry_run=False,
        verbose=False,
    )

    # Assert files created
    assert (tmp_path / ".myeditor/config.json").exists()

    # Verify content
    with open(tmp_path / ".myeditor/config.json") as f:
        config = json.load(f)
        assert config["title"] == "Test Project"


def test_myeditor_sync(tmp_path, sample_prompt):
    """Test syncing from MyEditor files."""
    adapter = MyEditorAdapter()

    # Create MyEditor files
    myeditor_dir = tmp_path / ".myeditor"
    myeditor_dir.mkdir()

    config = {"title": "Test", "content": "# Content"}
    with open(myeditor_dir / "config.json", "w") as f:
        json.dump(config, f)

    # Parse back to UPF
    parsed = adapter.parse_files(tmp_path)

    assert parsed.metadata.title == "Test"
    assert "# Content" in parsed.content
```

4. **Update documentation**:
   - Add to `docs/user-guide/adapters/index.md`
   - Create `docs/user-guide/adapters/myeditor.md` with usage examples

### Testing Your Contributions

#### Local Testing

```bash
# Run specific test file
pytest tests/unit/test_cli.py

# Run tests with verbose output
pytest -v

# Run tests for specific functionality
pytest -k "test_generate"

# Watch mode (requires pytest-watch)
pytest-watch
```

#### Integration Testing

Test CLI commands manually:

```bash
# Test init
promptrek init --output test.promptrek.yaml

# Test validate
promptrek validate test.promptrek.yaml

# Test generate
promptrek generate test.promptrek.yaml --editor myeditor --dry-run
```

#### Manual Testing

Test your changes with real-world scenarios:

1. Create a test project
2. Generate prompts for multiple editors
3. Verify the generated files work in actual editors
4. Test edge cases and error conditions

## Pull Request Process

### Before Submitting

- [ ] All tests pass locally
- [ ] Code follows style guidelines (Black, isort, flake8, mypy)
- [ ] Documentation is updated
- [ ] Commit messages follow conventional format
- [ ] Changes are focused and atomic
- [ ] No unrelated changes included

### PR Requirements

- **Clear title and description**
- **Link to related issues** (Fixes #123, Closes #456)
- **Include testing instructions**
- **Add screenshots for UI changes**
- **Request appropriate reviewers**
- **Mark as draft if work in progress**

### Review Process

1. **Automated checks** must pass (CI/CD)
2. **Code review** by maintainers
3. **Testing** on multiple platforms (handled by CI)
4. **Documentation review** if applicable
5. **Approval and merge** by maintainer

Expect feedback and be prepared to make changes. Reviews help maintain code quality and consistency.

## Release Process

PrompTrek uses semantic versioning and automated releases:

- **Patch** (1.0.1): Bug fixes
- **Minor** (1.1.0): New features, backward compatible
- **Major** (2.0.0): Breaking changes

Releases are automated based on conventional commits. See [Changelog Process](changelog-process.md) for details.

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Maintain professional communication
- Follow our [Code of Conduct](../../CODE_OF_CONDUCT.md)

### Getting Help

- **Documentation**: Start with this guide and the user documentation
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use [GitHub Discussions](https://github.com/flamingquaks/promptrek/discussions) for questions
- **Reviews**: Be patient and provide constructive feedback

### Recognition

Contributors are recognized in:
- Release notes and changelogs
- Repository contributors list
- Documentation acknowledgments
- Special thanks in release announcements

## Contribution Ideas

### Good First Issues

Perfect for newcomers:

- Fix typos in documentation
- Add examples for existing features
- Improve error messages
- Add unit tests for existing functionality
- Update outdated documentation

### Intermediate Contributions

For developers with some experience:

- Add new CLI options to existing commands
- Improve validation error messages
- Add support for new variable types
- Enhance test coverage
- Improve performance

### Advanced Contributions

For experienced developers:

- Add support for new AI editors
- Implement advanced template features
- Optimize performance for large configurations
- Add new CLI commands
- Design and implement new schema features

### Documentation

Always appreciated:

- Create video tutorials
- Write blog posts about use cases
- Translate documentation
- Improve API documentation
- Create integration guides

## Useful Resources

- [System Architecture](architecture.md)
- [Project Structure](project-structure.md)
- [Changelog Process](changelog-process.md)
- [UPF Specification](../user-guide/upf-specification.md)

## Contact

- **Issues**: [GitHub Issues](https://github.com/flamingquaks/promptrek/issues)
- **Discussions**: [GitHub Discussions](https://github.com/flamingquaks/promptrek/discussions)
- **Repository**: [GitHub Repository](https://github.com/flamingquaks/promptrek)

Thank you for contributing to PrompTrek! Your efforts help make AI-assisted development more accessible and consistent for developers everywhere.
