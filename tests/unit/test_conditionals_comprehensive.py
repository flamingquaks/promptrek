"""Comprehensive conditionals tests."""

import pytest
from promptrek.utils.conditionals import ConditionalProcessor
from promptrek.core.models import UniversalPrompt, PromptMetadata, Instructions, Condition


class TestConditionalProcessorComprehensive:
    """Comprehensive tests for ConditionalProcessor."""

    @pytest.fixture
    def processor(self):
        return ConditionalProcessor()

    def test_process_simple_condition_true(self, processor):
        """Test processing simple condition that's true."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["claude"],
            instructions=Instructions(general=["Base instruction"]),
            conditions=[
                Condition.model_validate({
                    "if": "EDITOR == 'claude'",
                    "then": {"instructions": {"general": ["Claude instruction"]}}
                })
            ]
        )
        
        result = processor.process_conditions(prompt, {"EDITOR": "claude"})
        assert result is not None

    def test_process_simple_condition_false(self, processor):
        """Test processing simple condition that's false."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["claude"],
            instructions=Instructions(general=["Base instruction"]),
            conditions=[
                Condition.model_validate({
                    "if": "EDITOR == 'cursor'",
                    "then": {"instructions": {"general": ["Cursor instruction"]}}
                })
            ]
        )
        
        result = processor.process_conditions(prompt, {"EDITOR": "claude"})
        assert result is not None

    def test_process_with_else_clause(self, processor):
        """Test processing condition with else clause."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["claude"],
            instructions=Instructions(general=["Base"]),
            conditions=[
                Condition.model_validate({
                    "if": "EDITOR == 'cursor'",
                    "then": {"instructions": {"general": ["Cursor"]}},
                    "else": {"instructions": {"general": ["Other"]}}
                })
            ]
        )
        
        result = processor.process_conditions(prompt, {"EDITOR": "claude"})
        assert result is not None
