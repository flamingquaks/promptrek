# Models Module

The models module defines the data structures for Universal Prompt Format (UPF) configurations using Pydantic for validation and serialization.

## Overview

PrompTrek uses Pydantic v2 models to represent UPF configurations. The module provides:

- **Multi-version schemas**: Support for UPF v1.x, v2.x, and v3.x
- **Type safety**: Full type hints for IDE support and type checking
- **Validation**: Automatic validation of field values and constraints
- **Serialization**: Easy conversion to/from dictionaries and JSON
- **Documentation**: Self-documenting models with field descriptions

### Model Hierarchy

```
BaseModel (Pydantic)
├── PromptMetadata
├── ProjectContext (v1)
├── Instructions (v1)
├── CustomCommand (v1)
├── EditorSpecificConfig (v1)
├── Condition (v1)
├── ImportConfig (v1)
├── DocumentConfig (v2/v3)
├── TrustMetadata (v2.1+)
├── MCPServer (v2.1+)
├── WorkflowStep (v3.1+)
├── Command (v2.1+)
├── Agent (v2.1+)
├── Hook (v2.1+)
├── PluginConfig (v2.1 - deprecated in v3)
├── UniversalPrompt (v1)
├── UniversalPromptV2 (v2)
├── UniversalPromptV3 (v3)
├── UserConfig
├── DynamicVariableConfig
└── GenerationMetadata
```

## API Reference

::: promptrek.core.models
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      docstring_style: google
      show_if_no_docstring: false

## Usage Examples

### Creating a V3 Prompt

Create a basic v3 UPF configuration:

```python
from promptrek.core.models import UniversalPromptV3, PromptMetadata

# Create metadata
metadata = PromptMetadata(
    title="Python API Project",
    description="AI assistant rules for Python API development",
    version="1.0.0",
    author="Your Name",
    tags=["python", "api", "fastapi"]
)

# Create v3 prompt
prompt = UniversalPromptV3(
    schema_version="3.0.0",
    metadata=metadata,
    content="""
# Python API Development Rules

## Code Style

- Use type hints for all function parameters and return values
- Follow PEP 8 style guidelines
- Use meaningful variable and function names

## Testing

- Write unit tests for all public functions
- Aim for >80% code coverage
- Use pytest for testing framework

## Documentation

- Document all public APIs with docstrings
- Use Google-style docstrings
- Include usage examples in docstrings
""".strip()
)

print(f"Created: {prompt.metadata.title}")
print(f"Schema: {prompt.schema_version}")
```

### Creating a V1 Prompt

Create a structured v1 UPF configuration:

```python
from promptrek.core.models import (
    UniversalPrompt,
    PromptMetadata,
    ProjectContext,
    Instructions
)

# Create a v1 prompt with structured instructions
prompt = UniversalPrompt(
    schema_version="1.0.0",
    metadata=PromptMetadata(
        title="Web Application Project",
        description="Full-stack web development rules"
    ),
    targets=["cursor", "copilot", "continue"],
    context=ProjectContext(
        project_type="web_application",
        technologies=["TypeScript", "React", "Node.js", "PostgreSQL"],
        description="Modern web application with React frontend and Node.js backend"
    ),
    instructions=Instructions(
        general=[
            "Write clean, maintainable code",
            "Follow TypeScript best practices",
            "Use functional programming patterns where appropriate"
        ],
        code_style=[
            "Use ESLint and Prettier for code formatting",
            "Prefer const over let, avoid var",
            "Use async/await instead of callbacks"
        ],
        testing=[
            "Write unit tests with Jest",
            "Write integration tests with Supertest",
            "Maintain >80% code coverage"
        ]
    ),
    variables={
        "PROJECT_NAME": "my-web-app",
        "API_VERSION": "v1",
        "DATABASE_NAME": "app_db"
    }
)

print(f"Targets: {', '.join(prompt.targets)}")
print(f"Technologies: {', '.join(prompt.context.technologies)}")
```

### Working with MCP Servers (V3)

Define MCP server configurations:

```python
from promptrek.core.models import (
    UniversalPromptV3,
    PromptMetadata,
    MCPServer,
    TrustMetadata
)

# Create MCP server configurations
mcp_servers = [
    MCPServer(
        name="filesystem",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"],
        description="Access project filesystem"
    ),
    MCPServer(
        name="github",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_TOKEN": "${GITHUB_TOKEN}"},
        description="GitHub repository access",
        trust_metadata=TrustMetadata(
            trusted=True,
            trust_level="partial",
            requires_approval=True,
            source="official"
        )
    )
]

# Create prompt with MCP servers
prompt = UniversalPromptV3(
    schema_version="3.0.0",
    metadata=PromptMetadata(
        title="Project with MCP",
        description="Configuration with MCP servers"
    ),
    content="# Development Rules\n\n- Follow best practices",
    mcp_servers=mcp_servers
)

# Access MCP servers
for server in prompt.mcp_servers:
    print(f"MCP Server: {server.name}")
    print(f"  Command: {server.command} {' '.join(server.args or [])}")
    if server.description:
        print(f"  Description: {server.description}")
```

### Working with Commands (V3)

Define custom slash commands:

```python
from promptrek.core.models import (
    UniversalPromptV3,
    PromptMetadata,
    Command,
    WorkflowStep
)

# Simple command
simple_command = Command(
    name="review-code",
    description="Review code for best practices",
    prompt="Review the selected code for:\n- Code style\n- Potential bugs\n- Performance issues",
    output_format="markdown"
)

# Multi-step workflow command
workflow_command = Command(
    name="create-pr",
    description="Create a GitHub pull request",
    prompt="Create a PR with proper formatting and checks",
    multi_step=True,
    tool_calls=["gh", "git", "read_file"],
    steps=[
        WorkflowStep(
            name="check-branch",
            action="execute_command",
            description="Verify current branch",
            params={"command": "git branch --show-current"}
        ),
        WorkflowStep(
            name="create-pr",
            action="execute_command",
            description="Create pull request",
            params={"command": "gh pr create --fill"}
        )
    ],
    requires_approval=False
)

# Create prompt with commands
prompt = UniversalPromptV3(
    schema_version="3.1.0",
    metadata=PromptMetadata(
        title="Commands Example",
        description="Custom workflow commands"
    ),
    content="# Project Rules",
    commands=[simple_command, workflow_command]
)

print(f"Commands: {len(prompt.commands)}")
for cmd in prompt.commands:
    print(f"  - /{cmd.name}: {cmd.description}")
```

### Working with Agents (V3)

Define autonomous agent configurations:

```python
from promptrek.core.models import (
    UniversalPromptV3,
    PromptMetadata,
    Agent,
    TrustMetadata
)

# Create agent configuration
code_reviewer = Agent(
    name="code-reviewer",
    prompt="""You are a senior code reviewer focused on:

- Code quality and maintainability
- Security best practices
- Performance optimization
- Test coverage

When reviewing code:
1. Identify potential bugs or issues
2. Suggest improvements
3. Highlight security concerns
4. Recommend additional tests

Be constructive and specific in your feedback.""",
    description="Automated code review assistant",
    tools=["read_file", "search_files", "analyze_code"],
    trust_level="partial",
    requires_approval=True,
    trust_metadata=TrustMetadata(
        trusted=False,
        trust_level="partial",
        requires_approval=True,
        source="local"
    )
)

# Create prompt with agent
prompt = UniversalPromptV3(
    schema_version="3.0.0",
    metadata=PromptMetadata(
        title="Code Review Agent",
        description="Automated code review"
    ),
    content="# Code Review Guidelines",
    agents=[code_reviewer]
)

print(f"Agent: {prompt.agents[0].name}")
print(f"Trust level: {prompt.agents[0].trust_level}")
```

### Working with Hooks (V3)

Define event-driven automation hooks:

```python
from promptrek.core.models import (
    UniversalPromptV3,
    PromptMetadata,
    Hook
)

# Create hooks
hooks = [
    Hook(
        name="pre-commit-lint",
        event="pre-commit",
        command="npm run lint && npm run test",
        description="Run linting and tests before commit"
    ),
    Hook(
        name="post-save-format",
        event="post-save",
        command="prettier --write {file}",
        description="Format file on save",
        conditions={"file_pattern": "*.{ts,tsx,js,jsx}"}
    ),
    Hook(
        name="prompt-submit-context",
        event="prompt-submit",
        command="git diff --cached",
        description="Include staged changes in context"
    )
]

# Create prompt with hooks
prompt = UniversalPromptV3(
    schema_version="3.0.0",
    metadata=PromptMetadata(
        title="Hooks Example",
        description="Event-driven automation"
    ),
    content="# Project Rules",
    hooks=hooks
)

for hook in prompt.hooks:
    print(f"Hook: {hook.name} (on {hook.event})")
```

### Working with Documents (V2/V3)

Create multi-document configurations:

```python
from promptrek.core.models import (
    UniversalPromptV3,
    PromptMetadata,
    DocumentConfig
)

# Main content
main_content = """
# General Development Rules

- Write clean, testable code
- Follow project conventions
- Document your code
"""

# Additional documents
documents = [
    DocumentConfig(
        name="python-rules",
        content="# Python Guidelines\n\n- Use type hints\n- Follow PEP 8",
        description="Python-specific rules",
        file_globs="**/*.py",
        always_apply=False
    ),
    DocumentConfig(
        name="typescript-rules",
        content="# TypeScript Guidelines\n\n- Use strict mode\n- Avoid any type",
        description="TypeScript-specific rules",
        file_globs="**/*.{ts,tsx}",
        always_apply=False
    ),
    DocumentConfig(
        name="security",
        content="# Security Guidelines\n\n- Validate all inputs\n- Use parameterized queries",
        description="Security best practices",
        always_apply=True
    )
]

# Create prompt
prompt = UniversalPromptV3(
    schema_version="3.0.0",
    metadata=PromptMetadata(
        title="Multi-Document Config",
        description="Rules organized by topic"
    ),
    content=main_content,
    documents=documents
)

print(f"Documents: {len(prompt.documents)}")
for doc in prompt.documents:
    print(f"  - {doc.name}")
    if doc.file_globs:
        print(f"    Applies to: {doc.file_globs}")
```

### Serialization and Deserialization

Work with model serialization:

```python
from promptrek.core.models import UniversalPromptV3, PromptMetadata
import json

# Create a prompt
prompt = UniversalPromptV3(
    schema_version="3.0.0",
    metadata=PromptMetadata(
        title="Test",
        description="Testing serialization"
    ),
    content="# Rules"
)

# Serialize to dict
data_dict = prompt.model_dump()
print("As dict:", data_dict)

# Serialize to JSON
json_str = prompt.model_dump_json(indent=2)
print("As JSON:", json_str)

# Deserialize from dict
new_prompt = UniversalPromptV3.model_validate(data_dict)
print(f"Deserialized: {new_prompt.metadata.title}")

# Deserialize from JSON
prompt_from_json = UniversalPromptV3.model_validate_json(json_str)
print(f"From JSON: {prompt_from_json.metadata.title}")
```

### Field Validation

Models automatically validate field values:

```python
from promptrek.core.models import UniversalPromptV3, PromptMetadata
from pydantic import ValidationError

try:
    # Invalid: empty content
    prompt = UniversalPromptV3(
        schema_version="3.0.0",
        metadata=PromptMetadata(
            title="Test",
            description="Test"
        ),
        content=""  # This will fail validation
    )
except ValidationError as e:
    print("Validation error:", e)

try:
    # Invalid: wrong schema version
    prompt = UniversalPromptV3(
        schema_version="2.0.0",  # Should be 3.x.x
        metadata=PromptMetadata(
            title="Test",
            description="Test"
        ),
        content="# Test"
    )
except ValidationError as e:
    print("Schema version error:", e)
```

### Using Variables

Access and work with variables:

```python
from promptrek.core.models import UniversalPromptV3, PromptMetadata

prompt = UniversalPromptV3(
    schema_version="3.0.0",
    metadata=PromptMetadata(
        title="Variables Example",
        description="Using template variables"
    ),
    content="Project: {{{ PROJECT_NAME }}}\nEnvironment: {{{ ENV }}}",
    variables={
        "PROJECT_NAME": "my-awesome-app",
        "ENV": "production",
        "API_URL": "https://api.example.com"
    }
)

# Access variables
print("Variables:")
for key, value in prompt.variables.items():
    print(f"  {key} = {value}")

# Check if variable exists
if "PROJECT_NAME" in prompt.variables:
    print(f"Project: {prompt.variables['PROJECT_NAME']}")
```

### Dynamic Variable Configuration

Define command-based dynamic variables:

```python
from promptrek.core.models import DynamicVariableConfig

# Static variable - just a string
static_var = "my-value"

# Dynamic variable - evaluated at runtime
dynamic_var = DynamicVariableConfig(
    type="command",
    value="git rev-parse --short HEAD",
    cache=True  # Cache result for session
)

print(f"Type: {dynamic_var.type}")
print(f"Command: {dynamic_var.value}")
print(f"Cache: {dynamic_var.cache}")
```

### User Configuration

User-specific settings (not committed to repo):

```python
from promptrek.core.models import UserConfig

# Create user config
user_config = UserConfig(
    schema_version="1.0.0",
    editor_paths={
        "cline_mcp_path": "/Users/myname/.config/cline/mcp.json",
        "cursor_rules_path": "/Users/myname/custom-rules"
    }
)

# Save to user-config.promptrek.yaml
import yaml
from pathlib import Path

config_dict = user_config.model_dump()
with open(".promptrek/user-config.promptrek.yaml", "w") as f:
    yaml.safe_dump(config_dict, f)
```

### Generation Metadata

Track generation runs for refresh command:

```python
from promptrek.core.models import GenerationMetadata, DynamicVariableConfig
from datetime import datetime

# Create generation metadata
metadata = GenerationMetadata(
    timestamp=datetime.now().isoformat(),
    source_file=".promptrek.yaml",
    editors=["cursor", "claude"],
    output_dir=".",
    variables={"PROJECT_NAME": "my-app"},
    dynamic_variables={
        "GIT_COMMIT": DynamicVariableConfig(
            type="command",
            value="git rev-parse --short HEAD",
            cache=True
        )
    },
    builtin_variables_enabled=True,
    allow_commands=True
)

# Save for refresh command
import yaml
from pathlib import Path

Path(".promptrek").mkdir(exist_ok=True)
with open(".promptrek/last-generation.yaml", "w") as f:
    yaml.safe_dump(metadata.model_dump(), f)
```

## Model Features

### Pydantic V2 Features

All models use Pydantic v2 features:

- **Field validation**: Automatic type checking and value validation
- **Field descriptions**: Self-documenting with Field(..., description=...)
- **Custom validators**: @field_validator for complex validation
- **Model validators**: @model_validator for cross-field validation
- **Serialization**: model_dump(), model_dump_json()
- **Deserialization**: model_validate(), model_validate_json()
- **Extra fields**: Controlled with extra="forbid" or extra="allow"

### Type Safety

Full type hints for IDE support:

```python
from typing import Optional, List, Dict
from promptrek.core.models import UniversalPromptV3

def process_prompt(prompt: UniversalPromptV3) -> List[str]:
    """Process a v3 prompt and return MCP server names."""
    if prompt.mcp_servers:
        return [server.name for server in prompt.mcp_servers]
    return []
```

## See Also

- [Parser Module](parser.md) - Parse YAML into models
- [Validator Module](validator.md) - Validate model instances
- [UPF Schema Reference](../../schema/index.md) - Complete schema documentation
- [Pydantic Documentation](https://docs.pydantic.dev/) - Pydantic library docs
