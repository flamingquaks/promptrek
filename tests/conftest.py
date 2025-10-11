"""Test configuration for pytest."""

import shutil
from pathlib import Path
from typing import Generator

import pytest

from promptrek.core.models import (
    Instructions,
    ProjectContext,
    PromptMetadata,
    UniversalPrompt,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_project_dir() -> Generator[Path, None, None]:
    """
    Create and clean up test-project/ directory for all tests.

    This ensures tests never pollute the project root with generated files.
    All file generation happens in test-project/ which is gitignored.
    """
    test_project_dir = Path(__file__).parent.parent / "test-project"

    # Clean up any existing test-project directory
    if test_project_dir.exists():
        shutil.rmtree(test_project_dir)

    # Create fresh test-project directory
    test_project_dir.mkdir(exist_ok=True)

    yield test_project_dir

    # Cleanup after all tests (optional - could keep for debugging)
    # if test_project_dir.exists():
    #     shutil.rmtree(test_project_dir)


@pytest.fixture(autouse=True)
def use_test_project_dir(
    setup_test_project_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
) -> None:
    """
    Automatically change to test-project/ directory for ALL tests.

    This is autouse=True so every test runs in test-project/ by default,
    preventing any test from polluting the project root.

    Tests can still use tmp_path, but the working directory will be test-project/.
    """
    # Skip this for tests that explicitly don't want it
    if "no_test_project" in request.keywords:
        return

    # Change working directory to test-project for this test
    monkeypatch.chdir(setup_test_project_dir)


@pytest.fixture
def test_project_root(setup_test_project_dir: Path, tmp_path: Path) -> Path:
    """
    Provide an isolated subdirectory within test-project/ for each test.

    This gives each test its own clean workspace while keeping everything
    organized under test-project/.

    Use this when you need a unique directory per test but still within test-project/.
    """
    # Create a unique subdirectory for this test
    test_dir = setup_test_project_dir / tmp_path.name
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir


@pytest.fixture
def sample_upf_data() -> dict:
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
