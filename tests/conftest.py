"""Test configuration for pytest."""

import pytest

from promptrek.core.models import (
    Instructions,
    ProjectContext,
    PromptMetadata,
    UniversalPrompt,
)


@pytest.fixture
def sample_upf_data():
    """Sample UPF data for testing."""
    return {
        "schema_version": "1.0.0",
        "metadata": {
            "title": "Test Project Assistant",
            "description": "AI assistant for testing",
            "version": "1.0.0",
            "author": "Test Author <test@example.com>",
            "created": "2024-01-01",
            "updated": "2024-01-01",
            "tags": ["test", "sample"],
        },
        "targets": ["copilot", "cursor"],
        "context": {
            "project_type": "web_application",
            "technologies": ["python", "javascript"],
            "description": "A test project",
        },
        "instructions": {
            "general": ["Write clean code", "Follow conventions"],
            "code_style": ["Use meaningful names", "Add comments"],
        },
        "examples": {"function": '```python\ndef hello():\n    return "world"\n```'},
        "variables": {"PROJECT_NAME": "Test Project", "AUTHOR": "Test Author"},
    }


@pytest.fixture
def sample_upf_file(tmp_path, sample_upf_data):
    """Create a temporary UPF file for testing."""
    import yaml

    file_path = tmp_path / "test.promptrek.yaml"
    with open(file_path, "w") as f:
        yaml.dump(sample_upf_data, f)

    return file_path


@pytest.fixture
def minimal_upf_data():
    """Minimal UPF data without optional fields like dates."""
    return {
        "schema_version": "1.0.0",
        "metadata": {
            "title": "Minimal Test Project",
            "description": "Minimal AI assistant for testing",
            "version": "1.0.0",
            "author": "Test Author <test@example.com>",
        },
        "targets": ["copilot", "cursor"],
    }


@pytest.fixture
def invalid_upf_data():
    """Invalid UPF data for testing."""
    return {
        "schema_version": "1.0.0",
        "metadata": {
            "title": "",  # Invalid: empty title
            "description": "Test description",
            "version": "1.0.0",
            "author": "Test Author",
            "created": "2024-01-01",
            "updated": "2024-01-01",
        },
        "targets": [],  # Invalid: no targets
    }


@pytest.fixture
def sample_prompt():
    """Create a sample UniversalPrompt object for testing."""
    return UniversalPrompt(
        schema_version="1.0.0",
        metadata=PromptMetadata(
            title="Test Project Assistant",
            description="AI assistant for testing",
            version="1.0.0",
            author="Test Author <test@example.com>",
            created="2024-01-01",
            updated="2024-01-01",
            tags=["test", "sample"],
        ),
        targets=["copilot", "cursor"],
        context=ProjectContext(
            project_type="web_application",
            technologies=["python", "javascript"],
            description="A test project",
        ),
        instructions=Instructions(
            general=["Write clean code", "Follow conventions"],
            code_style=["Use meaningful names", "Add comments"],
        ),
        examples={"function": '```python\ndef hello():\n    return "world"\n```'},
        variables={"PROJECT_NAME": "Test Project", "AUTHOR": "Test Author"},
    )
