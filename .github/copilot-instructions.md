# GitHub Copilot Instructions

This document contains merged GitHub Copilot instructions from 2 configuration files.

## Configuration Sources
1. **My Project Assistant** (`test-final.promptrek.yaml`) - AI assistant configuration for my project
2. **PrompTrek AI Editor Prompts** (`.promptrek.yaml`) - AI assistant configuration for developing PrompTrek - Universal AI Editor prompt management tool

## 1. My Project Assistant

*Source: `test-final.promptrek.yaml`*

AI assistant configuration for my project

### Instructions
#### General
- Write clean, readable, and maintainable code
- Follow existing code patterns and conventions
- Add appropriate comments for complex logic

#### Code Style
- Use meaningful and descriptive variable names
- Follow the existing linting and formatting rules
- Prefer explicit over implicit code

#### Testing
- Write unit tests for new functions
- Ensure tests are clear and well-documented
- Aim for good test coverage

---

## 2. PrompTrek AI Editor Prompts

*Source: `.promptrek.yaml`*

AI assistant configuration for developing PrompTrek - Universal AI Editor prompt management tool

### Instructions
#### General
- Follow Python best practices and PEP 8 conventions
- Use type hints for all function signatures and class attributes
- Write comprehensive docstrings following Google/NumPy style
- Maintain backward compatibility with Python 3.9+
- Follow the existing adapter pattern for new AI editor integrations
- Use Pydantic models for data validation and serialization
- Implement proper error handling with custom exceptions
- You are trying to update the PrompTrek project itself, not generated outputs

#### Code Style
- Format code with Black (line length 88)
- Sort imports with isort using Black profile
- Use type annotations for all functions and methods
- Prefer pathlib.Path over os.path for file operations
- Use click.echo() instead of print() for CLI output
- Follow naming conventions: snake_case for functions/variables, PascalCase for classes
- Use f-strings for string formatting when possible

#### Architecture
- Follow the adapter pattern: inherit from EditorAdapter base class
- Keep core models in src/promptrek/core/models.py using Pydantic
- Implement CLI commands in src/promptrek/cli/commands/ directory
- Use dependency injection and avoid tight coupling between components
- Separate concerns: parsing, validation, generation, and CLI interface
- Each adapter should handle one specific AI editor type
- Use registry pattern for adapter discovery and management

#### Testing
- Write unit tests for all public methods and functions
- Use pytest fixtures for common test setup
- Mock external dependencies and file operations in tests
- Test both success and failure scenarios
- Maintain 80%+ code coverage
- Write integration tests for CLI commands
- Use parametrized tests for testing multiple adapter types

#### Security
- Validate all user inputs using Pydantic models
- Sanitize file paths to prevent directory traversal
- Use safe YAML loading (yaml.safe_load)
- Validate file permissions before writing files

#### Performance
- Use lazy loading for adapter imports
- Cache compiled regex patterns
- Minimize file I/O operations in loops
- Use generators for large data processing
