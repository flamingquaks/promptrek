# Contributing to PrompTrek

Thank you for your interest in contributing to PrompTrek! This document provides guidelines for contributing to the project.

## Development Setup

1. Fork the repository
2. Clone your fork locally
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Code Quality Standards

### Formatting and Linting

Before submitting code, ensure it meets our quality standards:

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

### Testing

All changes should include appropriate tests:

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run all tests with coverage
pytest --cov=src/promptrek --cov-fail-under=80
```

## Commit Guidelines

We follow conventional commit messages:

```
type(scope): description

[optional body]

[optional footer]
```

**Types**: feat, fix, docs, style, refactor, test, chore
**Scopes**: cli, core, adapters, templates, docs

**Examples**:
- `feat(adapters): add Cursor editor support`
- `fix(parser): handle empty instructions gracefully`
- `docs(guides): add Copilot setup instructions`

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes following the code quality standards
3. Add or update tests as needed
4. Update documentation if applicable
5. Submit a pull request with a clear description

## Automated Testing

All pull requests will be tested automatically with:
- Code formatting checks (black, isort)
- Linting (flake8)
- Type checking (mypy)
- Unit and integration tests
- Coverage reporting
- Security scanning

## Getting Help

If you have questions or need help:
- Check existing issues and discussions
- Create a new issue with the appropriate template
- Reach out to maintainers

Thank you for contributing!