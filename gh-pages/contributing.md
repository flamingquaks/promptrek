---
layout: default
title: Contributing
---

# Contributing to PrompTrek

Thank you for your interest in contributing to PrompTrek! This guide will help you get started with contributing to the project.

## 🚀 Quick Start for Contributors

### Prerequisites

- Python 3.9 or higher
- Git
- A GitHub account

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

## 🎯 Ways to Contribute

### 🐛 Bug Reports

Found a bug? Help us fix it!

1. **Search existing issues** to avoid duplicates
2. **Create a new issue** using our bug report template
3. **Include detailed information:**
   - PrompTrek version
   - Python version
   - Operating system
   - Steps to reproduce
   - Expected vs actual behavior
   - Any error messages

[**Report a Bug →**]({{ site.issues_url }}/new?template=bug_report.yml)

### 💡 Feature Requests

Have an idea for a new feature?

1. **Check the roadmap** in our [Implementation Roadmap](https://github.com/flamingquaks/promptrek/blob/main/docs/IMPLEMENTATION_ROADMAP.md)
2. **Search existing issues** for similar requests
3. **Create a feature request** using our template
4. **Describe the use case** and expected benefits

[**Request a Feature →**]({{ site.issues_url }}/new?template=feature_request.yml)

### 🔧 Code Contributions

Ready to write some code? Here's how:

#### 1. Choose an Issue
- Look for issues labeled `good first issue` for beginners
- Check issues labeled `help wanted` for areas needing assistance
- Comment on the issue to express interest

#### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

#### 3. Make Your Changes
- Follow our [coding standards](#coding-standards)
- Write or update tests as needed
- Update documentation if necessary

#### 4. Test Your Changes
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=promptrek --cov-report=html

# Run linting
uv run black src/ tests/
uv run flake8 src/ tests/
uv run mypy src/
```

#### 5. Commit Your Changes
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
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

#### 6. Push and Create Pull Request
```bash
git push origin your-branch-name
```

Then create a pull request on GitHub using our PR template.

### 📝 Documentation

Documentation improvements are always welcome!

- **Fix typos or unclear explanations**
- **Add examples and use cases**
- **Improve API documentation**
- **Create tutorials or guides**
- **Update this website**

### 🎨 New Editor Support

Want to add support for a new AI editor?

1. **Research the editor's prompt format**
2. **Create an issue** to discuss the implementation
3. **Follow our adapter pattern** (see `src/promptrek/adapters/`)
4. **Add comprehensive tests**
5. **Update documentation**

See our [Editor Research](https://github.com/flamingquaks/promptrek/blob/main/docs/EDITOR_RESEARCH.md) for examples.

## 🛠 Development Guidelines

### Coding Standards

#### Code Quality
- **Type Hints**: All public functions must have type hints
- **Docstrings**: All public classes and functions need docstrings
- **Error Handling**: Use proper exception handling with custom exceptions
- **Logging**: Use structured logging throughout the application

#### Code Style
We use automated tools to maintain consistent code style:

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

#### Testing Standards
- **Coverage**: Maintain minimum 90% test coverage
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test complete workflows
- **Fixtures**: Use reusable test data and configurations

```bash
# Run tests with coverage
pytest --cov=promptrek --cov-report=html --cov-fail-under=90
```

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
├── docs/                        # Documentation
├── examples/                    # Example configurations
└── scripts/                     # Development scripts
```

### Adding a New Editor Adapter

1. **Create the adapter class** in `src/promptrek/adapters/`:
   ```python
   from .base import EditorAdapter
   
   class NewEditorAdapter(EditorAdapter):
       def generate(self, prompt, output_dir, **kwargs):
           # Implementation here
           pass
   ```

2. **Register the adapter** in `src/promptrek/core/registry.py`

3. **Add comprehensive tests** in `tests/unit/adapters/`

4. **Update documentation** and examples

### Testing Your Contributions

#### Local Testing
```bash
# Run specific test file
pytest tests/unit/test_cli.py

# Run tests with verbose output
pytest -v

# Run tests for specific functionality
pytest -k "test_generate"
```

#### Integration Testing
```bash
# Test CLI commands
promptrek init --output test.promptrek.yaml
promptrek validate test.promptrek.yaml
promptrek generate --all --input test.promptrek.yaml --dry-run
```

#### Manual Testing
Test your changes with real-world scenarios:

1. Create a test project
2. Generate prompts for multiple editors
3. Verify the generated files work in actual editors
4. Test edge cases and error conditions

## 📋 Pull Request Process

### Before Submitting
- [ ] All tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commit messages follow conventional format
- [ ] Changes are focused and atomic

### PR Requirements
- **Clear title and description**
- **Link to related issues**
- **Include testing instructions**
- **Add screenshots for UI changes**
- **Request appropriate reviewers**

### Review Process
1. **Automated checks** must pass (CI/CD)
2. **Code review** by maintainers
3. **Testing** on multiple platforms
4. **Documentation review** if applicable
5. **Approval and merge**

## 🏷 Release Process

PrompTrek uses semantic versioning and automated releases:

- **Patch** (1.0.1): Bug fixes
- **Minor** (1.1.0): New features, backward compatible
- **Major** (2.0.0): Breaking changes

Releases are automated based on conventional commits.

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Maintain professional communication

### Getting Help
- **Documentation**: Start with this guide and the user documentation
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Reviews**: Be patient and provide constructive feedback

### Recognition
Contributors are recognized in:
- Release notes and changelogs
- Repository contributors list
- Documentation acknowledgments

## 🎯 Contribution Ideas

### Good First Issues
- Fix typos in documentation
- Add examples for existing features
- Improve error messages
- Add unit tests for existing functionality

### Advanced Contributions
- Add support for new AI editors
- Implement advanced template features
- Optimize performance for large configurations
- Add new CLI commands or options

### Documentation
- Create video tutorials
- Write blog posts about use cases
- Translate documentation
- Improve API documentation

## 🔗 Useful Resources

- [Implementation Roadmap](https://github.com/flamingquaks/promptrek/blob/main/docs/IMPLEMENTATION_ROADMAP.md)
- [System Architecture](https://github.com/flamingquaks/promptrek/blob/main/docs/ARCHITECTURE.md)
- [UPF Specification](https://github.com/flamingquaks/promptrek/blob/main/docs/UPF_SPECIFICATION.md)
- [Editor Research](https://github.com/flamingquaks/promptrek/blob/main/docs/EDITOR_RESEARCH.md)

## 📞 Contact

- **Issues**: [GitHub Issues]({{ site.issues_url }})
- **Discussions**: [GitHub Discussions](https://github.com/flamingquaks/promptrek/discussions)
- **Repository**: [GitHub Repository]({{ site.github_url }})

---

Thank you for contributing to PrompTrek! Your efforts help make AI-assisted development more accessible and consistent for developers everywhere. 🚀