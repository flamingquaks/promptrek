# Conditionals Utility

The conditionals utility module processes conditional instructions in Universal Prompt Format files, allowing dynamic content based on variables and context.

## Overview

The `ConditionalProcessor` class enables conditional logic in UPF v1 prompts:

- **Variable-based conditions**: Evaluate conditions based on variable values
- **Editor targeting**: Conditional content for specific editors
- **Environment switching**: Different instructions for different environments
- **Technology-specific rules**: Apply rules based on project technologies
- **Boolean logic**: Support for equality, inequality, and set membership checks
- **Content merging**: Intelligently merge conditional content into prompts

Conditional instructions allow a single UPF file to adapt to different contexts without duplication.

## API Reference

::: promptrek.utils.conditionals
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      docstring_style: google
      show_if_no_docstring: false

## Usage Examples

### Basic Conditional Processing

Process conditions in a UPF prompt:

```python
from promptrek.core.parser import UPFParser
from promptrek.utils.conditionals import ConditionalProcessor

# Parse UPF with conditions
parser = UPFParser()
prompt = parser.parse_file(".promptrek.yaml")

# Process conditions
processor = ConditionalProcessor()
additional_content = processor.process_conditions(
    prompt,
    variables={"ENVIRONMENT": "production", "EDITOR": "cursor"}
)

print("Additional content from conditions:")
print(additional_content)
```

### Equality Conditions

Check if a variable equals a value:

```python
from promptrek.core.models import (
    UniversalPrompt,
    PromptMetadata,
    Condition
)
from promptrek.utils.conditionals import ConditionalProcessor

# Create prompt with condition
prompt = UniversalPrompt(
    schema_version="1.0.0",
    metadata=PromptMetadata(
        title="Conditional Test",
        description="Testing equality conditions"
    ),
    targets=["cursor"],
    conditions=[
        Condition(
            if_condition='ENVIRONMENT == "production"',
            then={
                "instructions": {
                    "security": [
                        "Enable all security checks",
                        "Use production API keys",
                        "Enable rate limiting"
                    ]
                }
            }
        )
    ]
)

# Process with production environment
processor = ConditionalProcessor()
content = processor.process_conditions(
    prompt,
    variables={"ENVIRONMENT": "production"}
)

# Condition matched - security instructions added
print(content)
# Output: {'instructions': {'security': [...]}}
```

### Inequality Conditions

Check if a variable does not equal a value:

```python
from promptrek.core.models import UniversalPrompt, PromptMetadata, Condition
from promptrek.utils.conditionals import ConditionalProcessor

prompt = UniversalPrompt(
    schema_version="1.0.0",
    metadata=PromptMetadata(
        title="Test",
        description="Inequality test"
    ),
    targets=["cursor"],
    conditions=[
        Condition(
            if_condition='ENVIRONMENT != "production"',
            then={
                "instructions": {
                    "general": [
                        "Debug mode enabled",
                        "Verbose logging enabled",
                        "Use development database"
                    ]
                }
            }
        )
    ]
)

processor = ConditionalProcessor()

# Development environment - condition matches
content = processor.process_conditions(
    prompt,
    variables={"ENVIRONMENT": "development"}
)
print("Development instructions added:", bool(content))

# Production environment - condition doesn't match
content = processor.process_conditions(
    prompt,
    variables={"ENVIRONMENT": "production"}
)
print("Production - no match:", len(content) == 0)
```

### Set Membership Conditions

Check if a variable is in a list of values:

```python
from promptrek.core.models import UniversalPrompt, PromptMetadata, Condition
from promptrek.utils.conditionals import ConditionalProcessor

prompt = UniversalPrompt(
    schema_version="1.0.0",
    metadata=PromptMetadata(
        title="Test",
        description="Set membership test"
    ),
    targets=["cursor"],
    conditions=[
        Condition(
            if_condition='EDITOR in ["cursor", "copilot", "claude"]',
            then={
                "instructions": {
                    "general": [
                        "Use inline suggestions",
                        "Enable autocomplete",
                        "Show documentation on hover"
                    ]
                }
            }
        )
    ]
)

processor = ConditionalProcessor()

# Cursor editor - in the list
content = processor.process_conditions(
    prompt,
    variables={"EDITOR": "cursor"}
)
print("Cursor matched:", bool(content))

# Unknown editor - not in list
content = processor.process_conditions(
    prompt,
    variables={"EDITOR": "vim"}
)
print("Vim matched:", bool(content))  # False
```

### If-Then-Else Conditions

Provide alternative content with else clause:

```python
from promptrek.core.models import UniversalPrompt, PromptMetadata, Condition
from promptrek.utils.conditionals import ConditionalProcessor

prompt = UniversalPrompt(
    schema_version="1.0.0",
    metadata=PromptMetadata(
        title="Test",
        description="If-then-else test"
    ),
    targets=["cursor"],
    conditions=[
        Condition(
            if_condition='ENVIRONMENT == "production"',
            then={
                "instructions": {
                    "general": ["Use production settings"]
                }
            },
            else_clause={
                "instructions": {
                    "general": ["Use development settings"]
                }
            }
        )
    ]
)

processor = ConditionalProcessor()

# Production - then branch
content = processor.process_conditions(
    prompt,
    variables={"ENVIRONMENT": "production"}
)
print(content["instructions"]["general"])
# Output: ['Use production settings']

# Development - else branch
content = processor.process_conditions(
    prompt,
    variables={"ENVIRONMENT": "development"}
)
print(content["instructions"]["general"])
# Output: ['Use development settings']
```

### Editor-Specific Conditions

Apply conditions based on target editor:

```python
from promptrek.core.models import UniversalPrompt, PromptMetadata, Condition
from promptrek.utils.conditionals import ConditionalProcessor

prompt = UniversalPrompt(
    schema_version="1.0.0",
    metadata=PromptMetadata(
        title="Editor Conditions",
        description="Editor-specific instructions"
    ),
    targets=["cursor", "copilot"],
    conditions=[
        Condition(
            if_condition='EDITOR == "cursor"',
            then={
                "instructions": {
                    "general": [
                        "Use Cursor AI features",
                        "Enable composer mode",
                        "Use Ctrl+K for inline edits"
                    ]
                }
            }
        ),
        Condition(
            if_condition='EDITOR == "copilot"',
            then={
                "instructions": {
                    "general": [
                        "Use GitHub Copilot suggestions",
                        "Enable Copilot Chat",
                        "Use inline completions"
                    ]
                }
            }
        )
    ]
)

processor = ConditionalProcessor()

# Adapters automatically add EDITOR to variables
content = processor.process_conditions(
    prompt,
    variables={"EDITOR": "cursor"}
)

print("Cursor-specific instructions:")
print(content["instructions"]["general"])
```

### Multiple Conditions

Process multiple conditional blocks:

```python
from promptrek.core.models import UniversalPrompt, PromptMetadata, Condition
from promptrek.utils.conditionals import ConditionalProcessor

prompt = UniversalPrompt(
    schema_version="1.0.0",
    metadata=PromptMetadata(
        title="Multiple Conditions",
        description="Multiple conditional blocks"
    ),
    targets=["cursor"],
    conditions=[
        # Condition 1: Environment
        Condition(
            if_condition='ENVIRONMENT == "production"',
            then={
                "instructions": {
                    "security": ["Enable security"]
                }
            }
        ),
        # Condition 2: Feature flag
        Condition(
            if_condition='FEATURE_X == "enabled"',
            then={
                "instructions": {
                    "general": ["Use Feature X"]
                }
            }
        ),
        # Condition 3: Editor
        Condition(
            if_condition='EDITOR == "cursor"',
            then={
                "instructions": {
                    "general": ["Use Cursor features"]
                }
            }
        )
    ]
)

processor = ConditionalProcessor()

# All conditions evaluated
content = processor.process_conditions(
    prompt,
    variables={
        "ENVIRONMENT": "production",
        "FEATURE_X": "enabled",
        "EDITOR": "cursor"
    }
)

# Multiple instruction lists merged
print("Security:", content["instructions"]["security"])
print("General:", content["instructions"]["general"])
# General list contains items from both matching conditions
```

### Content Merging

Conditional content is intelligently merged:

```python
from promptrek.core.models import UniversalPrompt, PromptMetadata, Condition
from promptrek.utils.conditionals import ConditionalProcessor

prompt = UniversalPrompt(
    schema_version="1.0.0",
    metadata=PromptMetadata(
        title="Merging Test",
        description="Test content merging"
    ),
    targets=["cursor"],
    conditions=[
        Condition(
            if_condition='LANG == "python"',
            then={
                "instructions": {
                    "general": ["Use type hints"],
                    "testing": ["Use pytest"]
                }
            }
        ),
        Condition(
            if_condition='FRAMEWORK == "fastapi"',
            then={
                "instructions": {
                    "general": ["Use async/await"],  # Merged with above
                    "code_style": ["Follow FastAPI patterns"]
                }
            }
        )
    ]
)

processor = ConditionalProcessor()

content = processor.process_conditions(
    prompt,
    variables={
        "LANG": "python",
        "FRAMEWORK": "fastapi"
    }
)

# Lists are extended
print("General instructions:")
for item in content["instructions"]["general"]:
    print(f"  - {item}")
# Output:
#   - Use type hints
#   - Use async/await

# New categories added
print("\nTesting instructions:")
print(content["instructions"]["testing"])
# Output: ['Use pytest']

print("\nCode style instructions:")
print(content["instructions"]["code_style"])
# Output: ['Follow FastAPI patterns']
```

### Boolean Variable Conditions

Use boolean variables directly:

```python
from promptrek.core.models import UniversalPrompt, PromptMetadata, Condition
from promptrek.utils.conditionals import ConditionalProcessor

prompt = UniversalPrompt(
    schema_version="1.0.0",
    metadata=PromptMetadata(
        title="Boolean Test",
        description="Boolean variable test"
    ),
    targets=["cursor"],
    conditions=[
        Condition(
            if_condition='ENABLE_DEBUG',
            then={
                "instructions": {
                    "general": [
                        "Enable verbose logging",
                        "Show debug information",
                        "Disable caching"
                    ]
                }
            }
        )
    ]
)

processor = ConditionalProcessor()

# Truthy variable - condition matches
content = processor.process_conditions(
    prompt,
    variables={"ENABLE_DEBUG": True}
)
print("Debug enabled:", bool(content))  # True

# Falsy variable - condition doesn't match
content = processor.process_conditions(
    prompt,
    variables={"ENABLE_DEBUG": False}
)
print("Debug disabled:", len(content) == 0)  # True
```

### Combining with Variable Substitution

Use conditions with variables:

```python
from promptrek.core.parser import UPFParser
from promptrek.utils.variables import VariableSubstitution
from promptrek.utils.conditionals import ConditionalProcessor

# UPF with both variables and conditions
yaml_content = """
schema_version: "1.0.0"
metadata:
  title: "Combined Example"
  description: "Variables and conditions together"
targets: ["cursor"]
variables:
  PROJECT_NAME: "my-app"
  ENVIRONMENT: "production"
conditions:
  - if: 'ENVIRONMENT == "production"'
    then:
      instructions:
        security:
          - "Enable security for {{{ PROJECT_NAME }}}"
          - "Use production API keys"
"""

# Parse
parser = UPFParser()
prompt = parser.parse_string(yaml_content)

# Process conditions
processor = ConditionalProcessor()
additional = processor.process_conditions(
    prompt,
    variables=prompt.variables
)

# Substitute variables in conditional content
sub = VariableSubstitution()
if additional.get("instructions", {}).get("security"):
    for i, instruction in enumerate(additional["instructions"]["security"]):
        additional["instructions"]["security"][i] = sub.substitute(
            instruction,
            prompt.variables
        )

print(additional["instructions"]["security"])
# Output:
#   ['Enable security for my-app', 'Use production API keys']
```

### Practical Example: Multi-Environment Setup

```yaml
# .promptrek.yaml
schema_version: "1.0.0"
metadata:
  title: "Multi-Environment Project"
  description: "Different rules per environment"
targets: ["cursor", "copilot"]

variables:
  PROJECT_NAME: "my-api"
  ENVIRONMENT: "development"

instructions:
  general:
    - "Follow REST API best practices"
    - "Write comprehensive tests"

conditions:
  # Development environment
  - if: 'ENVIRONMENT == "development"'
    then:
      instructions:
        general:
          - "Enable hot reload"
          - "Use local database"
          - "Verbose logging enabled"

  # Staging environment
  - if: 'ENVIRONMENT == "staging"'
    then:
      instructions:
        general:
          - "Test against staging API"
          - "Use staging database"
          - "Enable performance monitoring"

  # Production environment
  - if: 'ENVIRONMENT == "production"'
    then:
      instructions:
        security:
          - "Enable all security features"
          - "Use production API keys"
          - "Enable rate limiting"
          - "Monitor for security issues"
        performance:
          - "Enable caching"
          - "Optimize database queries"
          - "Monitor performance metrics"
```

Process for different environments:

```python
from promptrek.core.parser import UPFParser
from promptrek.utils.conditionals import ConditionalProcessor

parser = UPFParser()
processor = ConditionalProcessor()

# Load base prompt
prompt = parser.parse_file(".promptrek.yaml")

# Generate for production
prod_content = processor.process_conditions(
    prompt,
    variables={"ENVIRONMENT": "production"}
)
print("Production adds:")
print(f"  Security: {len(prod_content['instructions']['security'])} rules")
print(f"  Performance: {len(prod_content['instructions']['performance'])} rules")

# Generate for development
dev_content = processor.process_conditions(
    prompt,
    variables={"ENVIRONMENT": "development"}
)
print("\nDevelopment adds:")
print(f"  General: {len(dev_content['instructions']['general'])} rules")
```

## Condition Expression Syntax

### Supported Operators

```python
# Equality
'VARIABLE == "value"'
'EDITOR == "cursor"'

# Inequality
'VARIABLE != "value"'
'ENVIRONMENT != "production"'

# Set membership
'EDITOR in ["cursor", "copilot"]'
'LANG in ["python", "javascript", "typescript"]'

# Boolean (variable name alone)
'DEBUG_MODE'
'ENABLE_FEATURE_X'
```

### Expression Format

- String values must be quoted with `"` or `'`
- Variable names are unquoted
- Whitespace around operators is optional
- List items are comma-separated
- Boolean expressions are just the variable name

## Limitations

Current conditional implementation has some limitations:

- No support for `and`, `or`, `not` logical operators
- No support for numeric comparisons (`<`, `>`, `<=`, `>=`)
- No support for nested conditions
- No support for function calls or complex expressions

For complex conditional logic, consider using multiple UPF files and selecting the appropriate one at generation time.

## See Also

- [Variables Module](variables.md) - Variable substitution
- [Models Module](../core/models.md) - Condition model definition
- [Conditionals Guide](../../user-guide/conditionals.md) - User guide for conditions
