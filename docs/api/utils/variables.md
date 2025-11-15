# Variables Utility

The variables utility module handles variable substitution, dynamic variable evaluation, and built-in variables.

## Overview

PrompTrek's variable system supports:

- **Static variables**: Simple key-value pairs defined in UPF files
- **Dynamic variables**: Command-based variables evaluated at runtime
- **Built-in variables**: Automatically provided variables (dates, git info, project context)
- **Environment variables**: System environment variable substitution
- **Template syntax**: `{{{ VARIABLE_NAME }}}` for template variables, `${VAR}` for environment variables
- **Security controls**: Command execution requires explicit permission
- **Caching**: Optional caching for expensive dynamic variables

The module provides `VariableSubstitution` for template processing, `CommandExecutor` for secure command execution, `DynamicVariable` for runtime evaluation, and `BuiltInVariables` for standard variables.

## API Reference

::: promptrek.utils.variables
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      docstring_style: google
      show_if_no_docstring: false

## Usage Examples

### Basic Variable Substitution

Substitute template variables in content:

```python
from promptrek.utils.variables import VariableSubstitution

sub = VariableSubstitution()

content = """
Project: {{{ PROJECT_NAME }}}
Version: {{{ VERSION }}}
Environment: {{{ ENV }}}
"""

variables = {
    "PROJECT_NAME": "my-awesome-app",
    "VERSION": "1.2.3",
    "ENV": "production"
}

result = sub.substitute(content, variables)
print(result)

# Output:
# Project: my-awesome-app
# Version: 1.2.3
# Environment: production
```

### Environment Variable Substitution

Substitute system environment variables:

```python
from promptrek.utils.variables import VariableSubstitution
import os

# Set environment variable
os.environ["DATABASE_URL"] = "postgresql://localhost/mydb"
os.environ["API_KEY"] = "secret123"

sub = VariableSubstitution()

content = """
Database: ${DATABASE_URL}
API Key: ${API_KEY}
User: ${USER}
"""

# Substitute environment variables
result = sub.substitute(
    content,
    variables={},
    env_variables=True
)

print(result)
# Output includes resolved environment variables
```

### Strict vs Non-Strict Mode

Handle undefined variables:

```python
from promptrek.utils.variables import VariableSubstitution
from promptrek.core.exceptions import TemplateError

sub = VariableSubstitution()

content = "Name: {{{ PROJECT_NAME }}}\nVersion: {{{ VERSION }}}"
variables = {"PROJECT_NAME": "myapp"}  # VERSION missing

# Strict mode - raises error
try:
    result = sub.substitute(content, variables, strict=True)
except TemplateError as e:
    print(f"Error: {e}")
    # Output: "Error: Undefined variable: VERSION"

# Non-strict mode - leaves undefined variables unchanged
result = sub.substitute(content, variables, strict=False)
print(result)
# Output:
# Name: myapp
# Version: {{{ VERSION }}}
```

### Substituting Entire Prompts

Substitute variables in a UniversalPrompt object:

```python
from promptrek.core.parser import UPFParser
from promptrek.utils.variables import VariableSubstitution

# Parse UPF with variables
parser = UPFParser()
prompt = parser.parse_file(".promptrek.yaml")

# Substitute all variables in the prompt
sub = VariableSubstitution()
substituted = sub.substitute_prompt(
    prompt,
    additional_variables={"ENVIRONMENT": "staging"},
    env_variables=True,
    strict=False
)

# All string fields in the prompt now have variables substituted
print(f"Title: {substituted.metadata.title}")
if substituted.instructions:
    print(f"Instructions: {substituted.instructions.general}")
```

### Loading Local Variables

Load variables from `.promptrek/variables.promptrek.yaml`:

```python
from promptrek.utils.variables import VariableSubstitution
from pathlib import Path

sub = VariableSubstitution()

# Load from current directory or parents
variables = sub.load_local_variables(search_dir=Path.cwd())

if variables:
    print("Loaded variables:")
    for key, value in variables.items():
        print(f"  {key} = {value}")
else:
    print("No variables file found")
```

### Loading and Evaluating All Variables

Load static, dynamic, and built-in variables:

```python
from promptrek.utils.variables import VariableSubstitution
from pathlib import Path

sub = VariableSubstitution()

# Load all variables
all_vars = sub.load_and_evaluate_variables(
    search_dir=Path.cwd(),
    allow_commands=True,      # Enable dynamic variables
    include_builtins=True,    # Include built-in variables
    verbose=True,             # Show what's happening
    clear_cache=False         # Keep cached values
)

print("\nAll variables:")
for key, value in all_vars.items():
    print(f"  {key} = {value}")
```

### Working with Dynamic Variables

Execute commands for dynamic variable values:

```python
from promptrek.utils.variables import (
    VariableSubstitution,
    DynamicVariable,
    CommandExecutor
)

# Create dynamic variable
commit_var = DynamicVariable(
    name="GIT_COMMIT",
    command="git rev-parse --short HEAD",
    cache=True  # Cache result
)

# Create executor with security controls
executor = CommandExecutor(
    allow_commands=True,  # Must be enabled
    timeout=5,           # 5 second timeout
    verbose=True         # Show command execution
)

# Evaluate the variable
commit_hash = commit_var.evaluate(executor)
print(f"Commit: {commit_hash}")

# Cached - won't execute again
commit_hash2 = commit_var.evaluate(executor)
assert commit_hash == commit_hash2
```

### Built-in Variables

Access automatically provided variables:

```python
from promptrek.utils.variables import BuiltInVariables

# Get all built-in variables
builtins = BuiltInVariables.get_all(verbose=True)

print("Built-in variables:")
for key, value in builtins.items():
    print(f"  {key} = {value}")

# Example output:
#   CURRENT_DATE = 2025-11-15
#   CURRENT_TIME = 14:30:45
#   CURRENT_DATETIME = 2025-11-15T14:30:45Z
#   CURRENT_YEAR = 2025
#   CURRENT_MONTH = 11
#   CURRENT_DAY = 15
#   PROJECT_NAME = my-project
#   PROJECT_ROOT = /path/to/project
#   GIT_BRANCH = main
#   GIT_COMMIT_SHORT = a1b2c3d
```

### Command Execution Security

CommandExecutor provides security controls:

```python
from promptrek.utils.variables import CommandExecutor
from promptrek.core.exceptions import TemplateError

# Disabled by default - safe
executor = CommandExecutor(allow_commands=False)

try:
    result = executor.execute("echo hello")
except TemplateError as e:
    print(f"Blocked: {e}")
    # Output: "Command execution is disabled..."

# Explicitly enable
executor = CommandExecutor(
    allow_commands=True,
    timeout=5,
    verbose=True
)

# Now commands can execute (with warning on first use)
result = executor.execute("echo hello")
print(f"Result: {result}")
```

### Dynamic Variable Configuration

Define dynamic variables in `.promptrek/variables.promptrek.yaml`:

```yaml
# Static variables
PROJECT_NAME: "my-app"
VERSION: "1.0.0"

# Dynamic variable (command-based)
GIT_COMMIT:
  type: "command"
  value: "git rev-parse --short HEAD"
  cache: true

GIT_BRANCH:
  type: "command"
  value: "git rev-parse --abbrev-ref HEAD"
  cache: true

CURRENT_USER:
  type: "command"
  value: "whoami"
  cache: false
```

Load and use:

```python
from promptrek.utils.variables import VariableSubstitution

sub = VariableSubstitution()

# Load variables (evaluates commands)
variables = sub.load_and_evaluate_variables(
    allow_commands=True,
    include_builtins=True,
    verbose=True
)

# Use in content
content = """
Project: {{{ PROJECT_NAME }}}
Commit: {{{ GIT_COMMIT }}}
Branch: {{{ GIT_BRANCH }}}
Date: {{{ CURRENT_DATE }}}
"""

result = sub.substitute(content, variables)
print(result)
```

### Extracting Variables from Content

Find all variable references in content:

```python
from promptrek.utils.variables import VariableSubstitution

sub = VariableSubstitution()

content = """
Project: {{{ PROJECT_NAME }}}
Version: {{{ VERSION }}}
Home: ${HOME}
User: ${USER}
"""

# Extract all variables
variables = sub.extract_variables(content)
print("Variables found:")
for var in variables:
    print(f"  - {var}")

# Output:
#   - PROJECT_NAME
#   - VERSION
#   - ${HOME}
#   - ${USER}
```

### Finding Undefined Variables

Check for missing variables before substitution:

```python
from promptrek.utils.variables import VariableSubstitution

sub = VariableSubstitution()

content = """
Name: {{{ PROJECT_NAME }}}
Version: {{{ VERSION }}}
Author: {{{ AUTHOR }}}
"""

available = {
    "PROJECT_NAME": "myapp",
    "VERSION": "1.0.0"
    # AUTHOR missing
}

# Find undefined
undefined = sub.get_undefined_variables(content, available)
print(f"Missing variables: {', '.join(undefined)}")
# Output: "Missing variables: AUTHOR"
```

### Variable Restoration (Bidirectional Sync)

Restore variable placeholders during sync:

```python
from promptrek.utils.variables import VariableSubstitution
from pathlib import Path

sub = VariableSubstitution()

# Original content with variables
original = """
Project: {{{ PROJECT_NAME }}}
Commit: {{{ GIT_COMMIT }}}
Date: {{{ CURRENT_DATE }}}
"""

# Generated content (variables were substituted)
generated = """
Project: my-awesome-app
Commit: a1b2c3d
Date: 2025-11-15
"""

# Restore variable placeholders
restored = sub.restore_variables_in_content(
    original_content=original,
    parsed_content=generated,
    source_dir=Path.cwd(),
    verbose=True
)

print(restored)
# Output: original content with {{{ }}} placeholders restored
```

### Command Timeout Handling

Handle long-running commands:

```python
from promptrek.utils.variables import CommandExecutor
from promptrek.core.exceptions import TemplateError

executor = CommandExecutor(
    allow_commands=True,
    timeout=2  # 2 second timeout
)

try:
    # This command takes too long
    result = executor.execute("sleep 10")
except TemplateError as e:
    print(f"Timeout: {e}")
    # Output: "Command timed out after 2s: sleep 10"
```

### Command Error Handling

Handle command failures:

```python
from promptrek.utils.variables import CommandExecutor
from promptrek.core.exceptions import TemplateError

executor = CommandExecutor(allow_commands=True)

try:
    # Command not found
    result = executor.execute("nonexistent-command")
except TemplateError as e:
    print(f"Error: {e}")
    # Output: "Command not found: nonexistent-command"

try:
    # Command fails (non-zero exit)
    result = executor.execute("ls /nonexistent")
except TemplateError as e:
    print(f"Error: {e}")
    # Shows exit code and error output
```

### Variable Migration

Handle deprecated variable file location:

```python
from promptrek.utils.variables import VariableSubstitution
from pathlib import Path

sub = VariableSubstitution()

# If old location exists: variables.promptrek.yaml (root)
# And new location doesn't exist: .promptrek/variables.promptrek.yaml
# User is prompted to migrate (interactive mode)

variables = sub.load_local_variables(Path.cwd())

# Non-interactive mode (CI/CD) auto-migrates silently
```

### Variable Naming Validation

Check variable name conventions:

```python
from promptrek.core.validator import UPFValidator

validator = UPFValidator()

# Validator checks UPPER_SNAKE_CASE
valid_names = [
    "PROJECT_NAME",      # ✓ Valid
    "API_KEY",           # ✓ Valid
    "DATABASE_URL",      # ✓ Valid
    "VERSION_2",         # ✓ Valid (numbers ok)
]

invalid_names = [
    "projectName",       # ✗ camelCase
    "project_name",      # ✗ lowercase
    "Project-Name",      # ✗ kebab-case
    "123_VAR",           # ✗ starts with number
]

# Validator reports invalid names as warnings
```

### Practical Example: Dynamic Build Info

Use variables for build metadata:

```yaml
# .promptrek/variables.promptrek.yaml
PROJECT_NAME: "my-app"

BUILD_COMMIT:
  type: "command"
  value: "git rev-parse --short HEAD"
  cache: true

BUILD_BRANCH:
  type: "command"
  value: "git rev-parse --abbrev-ref HEAD"
  cache: true

BUILD_DATE:
  type: "command"
  value: "date -u +%Y-%m-%dT%H:%M:%SZ"
  cache: false  # Always fresh

BUILD_USER:
  type: "command"
  value: "git config user.name"
  cache: true
```

Use in UPF:

```yaml
schema_version: "3.0.0"
metadata:
  title: "{{{ PROJECT_NAME }}}"
  description: "Built on {{{ BUILD_DATE }}}"
content: |
  # Project Info

  - **Commit**: {{{ BUILD_COMMIT }}}
  - **Branch**: {{{ BUILD_BRANCH }}}
  - **Built by**: {{{ BUILD_USER }}}
  - **Built on**: {{{ BUILD_DATE }}}
```

Generate with variables:

```python
from promptrek.core.parser import UPFParser
from promptrek.utils.variables import VariableSubstitution
from promptrek.adapters.registry import registry

# Parse and load variables
parser = UPFParser()
prompt = parser.parse_file(".promptrek.yaml")

sub = VariableSubstitution()
variables = sub.load_and_evaluate_variables(
    allow_commands=True,
    include_builtins=True
)

# Generate with substitution
adapter = registry.get("cursor")
files = adapter.generate(
    prompt,
    output_dir=Path("."),
    variables=variables
)
```

## Variable Syntax

### Template Variables

```
{{{ VARIABLE_NAME }}}
```

- Three curly braces on each side
- Optional whitespace around name
- Uppercase snake_case recommended

### Environment Variables

```
${VARIABLE_NAME}
```

- Dollar sign with single curly braces
- Standard shell syntax
- Resolved from process environment

## Security Considerations

### Command Execution

Dynamic variables execute shell commands with these protections:

1. **Disabled by default**: `allow_commands: false` by default
2. **Explicit opt-in**: Must set `allow_commands: true` in UPF
3. **User warnings**: Shows warning on first command execution
4. **Timeout protection**: Commands timeout after 5 seconds
5. **Error handling**: Command failures are caught and reported

### Best Practices

- Only use dynamic variables from trusted sources
- Review `.promptrek/variables.promptrek.yaml` before enabling
- Use `cache: true` for variables that don't change
- Set appropriate timeouts for slow commands
- Handle command failures gracefully

## See Also

- [Conditionals Module](conditionals.md) - Conditional logic
- [Models Module](../core/models.md) - Variable models
- [Variables Guide](../../user-guide/variables.md) - User guide for variables
- [Dynamic Variables](../../user-guide/dynamic-variables.md) - Dynamic variable guide
