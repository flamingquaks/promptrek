"""
Variable substitution utilities for Agent Prompt Mapper.

Handles variable replacement in templates and UPF content.
"""

import re
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import os

from ..core.models import UniversalPrompt
from ..core.exceptions import TemplateError


class VariableSubstitution:
    """Handles variable substitution in templates and content."""
    
    def __init__(self):
        """Initialize variable substitution system."""
        self.variable_pattern = re.compile(r'\{\{\{\s*(\w+)\s*\}\}\}')
        self.env_pattern = re.compile(r'\$\{(\w+)\}')
    
    def substitute(self, content: str, variables: Dict[str, Any], 
                  env_variables: bool = True, strict: bool = False) -> str:
        """
        Substitute variables in content.
        
        Args:
            content: The content to process
            variables: Dictionary of variable values
            env_variables: Whether to substitute environment variables
            strict: If True, raise error for undefined variables
            
        Returns:
            Content with variables substituted
            
        Raises:
            TemplateError: If strict mode and undefined variables found
        """
        result = content
        
        # Substitute template variables (e.g., {{{ VARIABLE_NAME }}})
        result = self._substitute_template_variables(result, variables, strict)
        
        # Substitute environment variables (e.g., ${VAR_NAME})
        if env_variables:
            result = self._substitute_env_variables(result, strict)
        
        return result
    
    def substitute_prompt(self, prompt: UniversalPrompt, 
                         additional_variables: Optional[Dict[str, Any]] = None,
                         env_variables: bool = True, strict: bool = False) -> UniversalPrompt:
        """
        Create a copy of the prompt with all variables substituted.
        
        Args:
            prompt: The universal prompt to process
            additional_variables: Additional variables to merge with prompt variables
            env_variables: Whether to substitute environment variables
            strict: If True, raise error for undefined variables
            
        Returns:
            New UniversalPrompt with variables substituted
        """
        # Combine variables from prompt and additional variables
        variables = prompt.variables.copy() if prompt.variables else {}
        if additional_variables:
            variables.update(additional_variables)
        
        # Create a copy of the prompt data using aliases for proper reconstruction
        prompt_dict = prompt.model_dump(by_alias=True)
        
        # Substitute variables in all string fields recursively
        prompt_dict = self._substitute_dict_recursive(prompt_dict, variables, env_variables, strict)
        
        # Create a new prompt instance with substituted values
        return UniversalPrompt.model_validate(prompt_dict)
    
    def get_undefined_variables(self, content: str, variables: Dict[str, Any]) -> List[str]:
        """
        Get list of undefined variables in content.
        
        Args:
            content: Content to analyze
            variables: Available variables
            
        Returns:
            List of undefined variable names
        """
        undefined = []
        
        # Check template variables
        for match in self.variable_pattern.finditer(content):
            var_name = match.group(1)
            if var_name not in variables:
                undefined.append(var_name)
        
        return list(set(undefined))
    
    def extract_variables(self, content: str) -> List[str]:
        """
        Extract all variable names from content.
        
        Args:
            content: Content to analyze
            
        Returns:
            List of variable names found
        """
        variables = []
        
        # Extract template variables
        for match in self.variable_pattern.finditer(content):
            variables.append(match.group(1))
        
        # Extract environment variables
        for match in self.env_pattern.finditer(content):
            variables.append(f"${{{match.group(1)}}}")
        
        return list(set(variables))
    
    def _substitute_template_variables(self, content: str, variables: Dict[str, Any], strict: bool) -> str:
        """Substitute template variables in content."""
        def replace_var(match):
            var_name = match.group(1)
            if var_name in variables:
                return str(variables[var_name])
            elif strict:
                raise TemplateError(f"Undefined variable: {var_name}")
            else:
                return match.group(0)  # Leave unchanged
        
        return self.variable_pattern.sub(replace_var, content)
    
    def _substitute_env_variables(self, content: str, strict: bool) -> str:
        """Substitute environment variables in content."""
        def replace_env(match):
            var_name = match.group(1)
            value = os.getenv(var_name)
            if value is not None:
                return value
            elif strict:
                raise TemplateError(f"Undefined environment variable: {var_name}")
            else:
                return match.group(0)  # Leave unchanged
        
        return self.env_pattern.sub(replace_env, content)
    
    def _substitute_dict_recursive(self, data: Any, variables: Dict[str, Any], 
                                 env_variables: bool, strict: bool) -> Any:
        """Recursively substitute variables in a dictionary/list structure."""
        if isinstance(data, str):
            return self.substitute(data, variables, env_variables, strict)
        elif isinstance(data, dict):
            return {k: self._substitute_dict_recursive(v, variables, env_variables, strict) 
                   for k, v in data.items()}
        elif isinstance(data, list):
            return [self._substitute_dict_recursive(item, variables, env_variables, strict) 
                   for item in data]
        else:
            return data