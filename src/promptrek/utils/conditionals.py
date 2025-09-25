"""
Conditional processing utilities for PromptTrek.

Handles conditional instructions and template logic in UPF content.
"""

import re
from typing import Any, Dict, Optional

from ..core.models import UniversalPrompt


class ConditionalProcessor:
    """Processes conditional instructions in UPF prompts."""

    def __init__(self) -> None:
        """Initialize conditional processor."""
        self.variable_pattern = re.compile(r"\{\{\{\s*(\w+)\s*\}\}\}")

    def process_conditions(
        self, prompt: UniversalPrompt, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process all conditional instructions in a prompt.

        Args:
            prompt: The universal prompt
            variables: Variables available for condition evaluation

        Returns:
            Dictionary of additional instructions to merge
        """
        if not prompt.conditions:
            return {}

        # Combine prompt variables with additional variables
        all_variables = prompt.variables.copy() if prompt.variables else {}
        if variables:
            all_variables.update(variables)

        # Process each condition
        additional_content: Dict[str, Any] = {}
        for condition in prompt.conditions:
            if self._evaluate_condition(condition.if_condition, all_variables):
                if condition.then:
                    self._merge_content(additional_content, condition.then)
            elif condition.else_clause:
                self._merge_content(additional_content, condition.else_clause)

        return additional_content

    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """
        Evaluate a condition expression.

        Supports basic expressions like:
        - VARIABLE == "value"
        - VARIABLE != "value"
        - VARIABLE in ["value1", "value2"]
        - EDITOR == "claude"

        Args:
            condition: The condition expression
            variables: Available variables

        Returns:
            True if condition is met, False otherwise
        """
        # Simple condition parsing - can be extended for more complex logic
        condition = condition.strip()

        # Handle equality checks
        if " == " in condition:
            left, right = condition.split(" == ", 1)
            left = left.strip()
            right = right.strip().strip("\"'")
            return str(variables.get(left, "")) == right

        # Handle inequality checks
        if " != " in condition:
            left, right = condition.split(" != ", 1)
            left = left.strip()
            right = right.strip().strip("\"'")
            return str(variables.get(left, "")) != right

        # Handle 'in' checks
        if " in " in condition:
            left, right = condition.split(" in ", 1)
            left = left.strip()
            # Parse list like ["value1", "value2"]
            if right.strip().startswith("[") and right.strip().endswith("]"):
                values = [
                    v.strip().strip("\"'") for v in right.strip()[1:-1].split(",")
                ]
                return str(variables.get(left, "")) in values

        # Handle boolean variables
        if condition in variables:
            return bool(variables[condition])

        # Default to False for unrecognized expressions
        return False

    def _merge_content(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Merge conditional content into target dictionary.

        Args:
            target: Target dictionary to merge into
            source: Source content to merge
        """
        for key, value in source.items():
            if key in target:
                # If both are lists, extend
                if isinstance(target[key], list) and isinstance(value, list):
                    target[key].extend(value)
                # If both are dicts, recurse
                elif isinstance(target[key], dict) and isinstance(value, dict):
                    self._merge_content(target[key], value)
                # Otherwise, replace
                else:
                    target[key] = value
            else:
                target[key] = value
