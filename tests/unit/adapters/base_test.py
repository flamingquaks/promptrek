"""
Base test class for editor adapters.
"""

import pytest

from src.apm.core.models import (
    UniversalPrompt, PromptMetadata, ProjectContext, Instructions
)


class TestAdapterBase:
    """Base test class for all adapters."""
    
    @pytest.fixture
    def sample_prompt(self):
        """Create a sample universal prompt for testing."""
        return UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="A test project for AI assistance",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
                tags=["test", "example"]
            ),
            targets=["copilot", "cursor", "continue"],
            context=ProjectContext(
                project_type="web_application",
                technologies=["typescript", "react", "nodejs"],
                description="A modern web application"
            ),
            instructions=Instructions(
                general=["Write clean, maintainable code", "Follow TypeScript best practices"],
                code_style=["Use consistent indentation", "Prefer const over let"],
                testing=["Write unit tests for all functions", "Use descriptive test names"]
            ),
            examples={
                "component": "const Button = ({ label }: { label: string }) => <button>{label}</button>;",
                "function": "export const formatDate = (date: Date): string => date.toISOString();"
            },
            variables={
                "project_name": "TestProject",
                "author_name": "Test Author"
            }
        )