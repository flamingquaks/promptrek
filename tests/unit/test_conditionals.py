"""
Unit tests for conditional processing.
"""

import pytest

from src.promptrek.core.models import Condition, PromptMetadata, UniversalPrompt
from src.promptrek.utils.conditionals import ConditionalProcessor


class TestConditionalProcessor:
    """Test conditional processing functionality."""

    @pytest.fixture
    def processor(self):
        """Create conditional processor instance."""
        return ConditionalProcessor()

    def test_evaluate_condition_equality(self, processor):
        """Test equality condition evaluation."""
        variables = {"EDITOR": "claude", "PROJECT_TYPE": "web"}

        assert processor._evaluate_condition('EDITOR == "claude"', variables) is True
        assert processor._evaluate_condition('EDITOR == "cursor"', variables) is False
        assert processor._evaluate_condition('PROJECT_TYPE == "web"', variables) is True

    def test_evaluate_condition_inequality(self, processor):
        """Test inequality condition evaluation."""
        variables = {"EDITOR": "claude", "MODE": "development"}

        assert processor._evaluate_condition('EDITOR != "cursor"', variables) is True
        assert processor._evaluate_condition('EDITOR != "claude"', variables) is False
        assert processor._evaluate_condition('MODE != "production"', variables) is True

    def test_evaluate_condition_in_list(self, processor):
        """Test 'in' condition evaluation."""
        variables = {"EDITOR": "claude", "LANG": "python"}

        assert (
            processor._evaluate_condition('EDITOR in ["claude", "cursor"]', variables)
            is True
        )
        assert (
            processor._evaluate_condition(
                'EDITOR in ["copilot", "continue"]', variables
            )
            is False
        )
        assert (
            processor._evaluate_condition('LANG in ["python", "javascript"]', variables)
            is True
        )

    def test_evaluate_condition_boolean(self, processor):
        """Test boolean condition evaluation."""
        variables = {"DEBUG": True, "VERBOSE": False, "STRICT": "true"}

        assert processor._evaluate_condition("DEBUG", variables) is True
        assert processor._evaluate_condition("VERBOSE", variables) is False
        assert processor._evaluate_condition("NONEXISTENT", variables) is False

    def test_merge_content_lists(self, processor):
        """Test merging list content."""
        target = {"instructions": ["general instruction"]}
        source = {"instructions": ["specific instruction"]}

        processor._merge_content(target, source)

        assert len(target["instructions"]) == 2
        assert "general instruction" in target["instructions"]
        assert "specific instruction" in target["instructions"]

    def test_merge_content_dicts(self, processor):
        """Test merging dictionary content."""
        target = {"config": {"setting1": "value1"}}
        source = {"config": {"setting2": "value2"}}

        processor._merge_content(target, source)

        assert target["config"]["setting1"] == "value1"
        assert target["config"]["setting2"] == "value2"

    def test_merge_content_replace(self, processor):
        """Test replacing content during merge."""
        target = {"title": "Original"}
        source = {"title": "Updated"}

        processor._merge_content(target, source)

        assert target["title"] == "Updated"

    def test_process_conditions_basic(self, processor):
        """Test processing basic conditions."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test prompt",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["claude"],
            conditions=[
                Condition(
                    **{"if": 'EDITOR == "claude"'},
                    then={"instructions": {"general": ["Claude-specific instruction"]}},
                )
            ],
        )

        variables = {"EDITOR": "claude"}
        result = processor.process_conditions(prompt, variables)

        assert "instructions" in result
        assert "general" in result["instructions"]
        assert "Claude-specific instruction" in result["instructions"]["general"]

    def test_process_conditions_with_else(self, processor):
        """Test processing conditions with else clause."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test prompt",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["cursor"],
            conditions=[
                Condition(
                    **{"if": 'EDITOR == "claude"'},
                    then={"message": "For Claude"},
                    **{"else": {"message": "For other editors"}},
                )
            ],
        )

        variables = {"EDITOR": "cursor"}
        result = processor.process_conditions(prompt, variables)

        assert result["message"] == "For other editors"

    def test_process_conditions_no_conditions(self, processor):
        """Test processing prompt with no conditions."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test prompt",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["claude"],
        )

        result = processor.process_conditions(prompt, {})
        assert result == {}

    def test_process_conditions_multiple(self, processor):
        """Test processing multiple conditions."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test prompt",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["claude"],
            conditions=[
                Condition(
                    **{"if": 'EDITOR == "claude"'},
                    then={"features": ["claude_feature"]},
                ),
                Condition(
                    **{"if": 'MODE == "development"'},
                    then={"features": ["debug_feature"]},
                ),
            ],
        )

        variables = {"EDITOR": "claude", "MODE": "development"}
        result = processor.process_conditions(prompt, variables)

        assert "features" in result
        assert "claude_feature" in result["features"]
        assert "debug_feature" in result["features"]
