# Contributing to PrompTrek

Thank you for your interest in contributing to PrompTrek! This guide will help you get started with contributing to the project.

## Quick Start for Contributors

### Prerequisites

- Python 3.9 or higher
- Git
- A GitHub account

### Development Setup

**1. Fork the repository** on GitHub

**2. Clone your fork locally:**
```bash
git clone https://github.com/YOUR_USERNAME/promptrek.git
cd promptrek
```

**3. Install development dependencies:**
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e ".[dev]"
```

**4. Install pre-commit hooks:**
```bash
pre-commit install
```

**5. Run tests to verify setup:**
```bash
# Using uv
uv run pytest

# Or using pytest directly
pytest
```

## Ways to Contribute

### Bug Reports

Found a bug? Help us fix it!

**Before reporting:**
1. Search [existing issues](https://github.com/flamingquaks/promptrek/issues) to avoid duplicates
2. Ensure you're using the latest version: `promptrek --version`

**Create a bug report:**

[Report a Bug](https://github.com/flamingquaks/promptrek/issues/new?template=bug_report.yml)

**Include:**
- PrompTrek version
- Python version (`python --version`)
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages (full stack trace if available)
- Minimal example configuration (if applicable)

### Feature Requests

Have an idea for a new feature?

**Before requesting:**
1. Search [existing issues](https://github.com/flamingquaks/promptrek/issues) for similar requests
2. Consider if it fits PrompTrek's scope and philosophy

**Create a feature request:**

[Request a Feature](https://github.com/flamingquaks/promptrek/issues/new?template=feature_request.yml)

**Describe:**
- The problem you're trying to solve
- Your proposed solution
- How it would benefit other users
- Alternative solutions you've considered
- Example usage or configuration

### Code Contributions

Ready to write some code? Here's how:

#### 1. Choose an Issue

**Good First Issues:**
- Look for [good first issue](https://github.com/flamingquaks/promptrek/labels/good%20first%20issue) label
- These are suitable for newcomers
- Clear requirements and scope

**Help Wanted:**
- Check [help wanted](https://github.com/flamingquaks/promptrek/labels/help%20wanted) label
- Areas where we need assistance

**Comment on the issue** to express interest before starting work.

#### 2. Create a Branch

```bash
# Create feature branch from main
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

**Branch naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/updates

#### 3. Make Your Changes

**Follow coding standards:**
- Type hints for all public functions
- Docstrings for all public classes and functions
- Proper error handling with custom exceptions
- Structured logging throughout

**Code style:**
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/ --max-line-length=88

# Type checking
mypy src/
```

#### 4. Test Your Changes

**Run tests:**
```bash
# All tests
uv run pytest

# With coverage
pytest --cov=src/promptrek --cov-report=html

# Specific test file
pytest tests/unit/test_cli.py

# Specific test
pytest tests/unit/test_cli.py::test_init_command
```

**Write tests:**
- Unit tests for individual functions/classes
- Integration tests for complete workflows
- Maintain minimum 90% coverage
- Use fixtures for reusable test data

**Example test:**
```python
def test_parse_valid_config():
    """Test parsing a valid configuration file."""
    parser = UPFParser()
    prompt = parser.parse_file("tests/fixtures/valid.yaml")

    assert prompt.metadata.title == "Test Project"
    assert prompt.content
    assert "PROJECT_NAME" in prompt.variables
```

#### 5. Update Documentation

**Update if you:**
- Add new features
- Change CLI commands
- Modify configuration schema
- Add new editor adapters

**Documentation types:**
- Code docstrings
- CLI help text
- User guide (in `docs/`)
- Examples (in `examples/`)
- README updates

#### 6. Commit Your Changes

We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: type(scope): description
git commit -m "feat(adapters): add support for new editor"
git commit -m "fix(parser): handle edge case in YAML parsing"
git commit -m "docs(readme): update installation instructions"
```

**Commit types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `perf`: Performance improvements

**Example commit message:**
```
feat(cli): add interactive wizard for project initialization

- Add guided workflow with prompts
- Auto-detect existing configurations
- Support multiple schema versions
- Include pre-commit hook setup

Closes #123
```

#### 7. Push and Create Pull Request

```bash
# Push to your fork
git push origin your-branch-name
```

**Create pull request on GitHub**

**PR Title:** Use conventional commit format
```
feat(adapters): add support for new editor
```

**PR Description:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [x] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Updated documentation

## Checklist
- [x] Code follows style guidelines
- [x] Self-reviewed code
- [x] Commented complex code
- [x] Updated documentation
- [x] No new warnings
- [x] Added tests
- [x] All tests pass
```

### Documentation

Documentation improvements are always welcome!

**What to improve:**
- Fix typos or unclear explanations
- Add examples and use cases
- Improve API documentation
- Create tutorials or guides
- Update this website
- Add translations (future)

**Where:**
- Code docstrings
- User guide (`docs/user-guide/`)
- Examples (`examples/`)
- Reference docs (`docs/reference/`)
- README files

### New Editor Support

Want to add support for a new AI editor?

**1. Research the editor's configuration format**
- Where does it store prompts/rules?
- What format does it use?
- What features does it support?

**2. Create an issue** to discuss the implementation

**3. Implement the adapter:**

```python
# src/promptrek/adapters/your_editor.py
from .base import EditorAdapter

class YourEditorAdapter(EditorAdapter):
    """Adapter for Your Editor."""

    def generate(self, prompt: UniversalPromptV3, output_dir: str, **kwargs):
        """Generate configuration files for Your Editor."""
        # Implementation here
        pass

    def sync(self, input_path: str) -> UniversalPromptV3:
        """Import configuration from Your Editor files."""
        # Implementation here
        pass
```

**4. Register the adapter** in `src/promptrek/core/registry.py`

**5. Add comprehensive tests** in `tests/unit/adapters/`

**6. Update documentation:**
- User guide
- Adapter capabilities matrix
- Examples

## Development Guidelines

### Project Structure

```
promptrek/
├── src/
│   └── promptrek/
│       ├── cli/                 # Command-line interface
│       ├── core/                # Core functionality
│       ├── adapters/            # Editor-specific adapters
│       ├── templates/           # Jinja2 templates
│       └── utils/               # Utility functions
├── tests/
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── fixtures/                # Test data
├── examples/                    # Example configurations
├── docs/                        # Documentation
└── scripts/                     # Development scripts
```

### Coding Standards

**Type Hints:**
```python
def parse_file(file_path: str) -> UniversalPromptV3:
    """Parse a PrompTrek configuration file."""
    pass
```

**Docstrings:**
```python
def generate(self, prompt: UniversalPromptV3, output_dir: str) -> None:
    """Generate editor-specific configuration files.

    Args:
        prompt: Parsed universal prompt configuration
        output_dir: Directory for generated files

    Raises:
        ValueError: If configuration is invalid
        IOError: If file writing fails
    """
    pass
```

**Error Handling:**
```python
from promptrek.core.exceptions import ValidationError

if not prompt.content:
    raise ValidationError("Content field is required")
```

**Logging:**
```python
import logging

logger = logging.getLogger(__name__)

logger.info("Generating configuration for %s", editor_name)
logger.debug("Using template: %s", template_path)
logger.error("Failed to generate: %s", error)
```

### Testing Standards

**Coverage:**
- Maintain minimum 90% test coverage
- Focus on critical paths first
- Test edge cases and error conditions

**Test Structure:**
```python
def test_feature_name():
    """Test description in imperative mood."""
    # Arrange
    parser = UPFParser()
    config = {"schema_version": "3.1.0", ...}

    # Act
    result = parser.parse_dict(config)

    # Assert
    assert result.schema_version == "3.1.0"
    assert result.metadata.title
```

**Fixtures:**
```python
# conftest.py
import pytest

@pytest.fixture
def valid_config():
    """Provide a valid configuration for testing."""
    return {
        "schema_version": "3.1.0",
        "metadata": {"title": "Test"},
        "content": "# Test",
    }
```

### Pull Request Process

**Before Submitting:**
- [ ] All tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commit messages follow conventional format
- [ ] Changes are focused and atomic
- [ ] No unrelated changes included

**PR Requirements:**
- Clear title and description
- Link to related issues
- Include testing instructions
- Add screenshots for UI changes
- Request appropriate reviewers

**Review Process:**
1. Automated checks must pass (CI/CD)
2. Code review by maintainers
3. Testing on multiple platforms (if applicable)
4. Documentation review
5. Approval and merge

**After Merge:**
- Your contribution will appear in the next release
- You'll be added to the contributors list
- Feature will be documented in changelog

## Release Process

PrompTrek uses semantic versioning and automated releases:

**Version Format:**
- **Patch** (1.0.1): Bug fixes
- **Minor** (1.1.0): New features, backward compatible
- **Major** (2.0.0): Breaking changes

**Releases are automated** based on conventional commits.

**Release candidates** use `-rc` suffix: `1.0.0-rc.1`

## Community Guidelines

### Code of Conduct

**Be Respectful:**
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Maintain professional communication
- Respect different perspectives

**Be Inclusive:**
- Use inclusive language
- Consider accessibility in contributions
- Welcome contributors of all skill levels

**Be Collaborative:**
- Credit others' work
- Share knowledge and resources
- Help review others' contributions

See our full [Code of Conduct](code-of-conduct.md).

### Getting Help

**For Contributors:**
- Read existing documentation
- Search issues and discussions
- Ask in [GitHub Discussions](https://github.com/flamingquaks/promptrek/discussions)
- Tag maintainers in comments (sparingly)

**Response Times:**
- Bug reports: 2-3 business days
- Feature requests: 1 week
- PR reviews: 3-5 business days

### Recognition

**Contributors are recognized in:**
- Release notes and changelogs
- Repository contributors list
- Documentation acknowledgments
- Social media announcements (with permission)

## Contribution Ideas

### Good First Issues

**For Beginners:**
- Fix typos in documentation
- Add examples for existing features
- Improve error messages
- Add unit tests for existing functionality
- Update outdated documentation

### Intermediate Contributions

**For Regular Contributors:**
- Add new editor adapters
- Implement advanced template features
- Optimize performance for large configurations
- Add new CLI commands or options
- Improve test coverage

### Advanced Contributions

**For Experienced Contributors:**
- Design new schema versions
- Implement complex features (workflows, automation)
- Performance profiling and optimization
- Architecture improvements
- New plugin systems

### Documentation

**Always Needed:**
- Create video tutorials
- Write blog posts about use cases
- Translate documentation (future)
- Improve API documentation
- Create interactive examples

## Resources

### Project Resources

- [System Architecture](https://flamingquaks.github.io/promptrek/developer/architecture.html)
- [UPF Specification](https://flamingquaks.github.io/promptrek/user-guide/upf-specification.html)
- [Project Structure](https://flamingquaks.github.io/promptrek/developer/project-structure.html)
- [Changelog Process](https://flamingquaks.github.io/promptrek/developer/changelog-process.html)

### Learning Resources

- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [YAML Specification](https://yaml.org/spec/)

## Contact

- **Issues:** [GitHub Issues](https://github.com/flamingquaks/promptrek/issues)
- **Discussions:** [GitHub Discussions](https://github.com/flamingquaks/promptrek/discussions)
- **Repository:** [GitHub Repository](https://github.com/flamingquaks/promptrek)

---

Thank you for contributing to PrompTrek! Your efforts help make AI-assisted development more accessible and consistent for developers everywhere.
