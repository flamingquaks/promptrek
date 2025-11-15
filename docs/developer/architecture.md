# System Architecture

PrompTrek's architecture is designed around a core conversion engine that transforms universal prompt configurations into editor-specific formats through an adapter pattern.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Universal      │    │   CLI Tool      │    │ Editor-Specific │
│  Prompt Files   │───▶│  (PrompTrek)    │───▶│ Prompt Files    │
│  (.promptrek.yaml)    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Adapters &     │
                       │  Templates      │
                       └─────────────────┘
```

## Core Components

### 1. Universal Prompt Format (UPF)

The UPF is a schema-versioned YAML format that serves as the single source of truth for prompt configurations.

**Current Schema (v3.0.0)**:
```yaml
schema_version: "3.0.0"

metadata:
  title: "Project Assistant"
  description: "AI configuration"
  version: "1.0.0"
  author: "Developer <dev@example.com>"
  created: "2024-01-01"
  updated: "2024-01-15"
  tags: ["project", "ai-assistant"]

content: |
  # Project Documentation

  Markdown-based instructions for AI assistants...

variables:
  PROJECT_NAME: "MyApp"
  VERSION: "1.0.0"

# Top-level plugin fields (v3.0.0+)
mcp_servers:
  - name: "filesystem"
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem"]

commands:
  - name: "/test"
    prompt: "Run tests for the current file"

agents:
  - name: "code-reviewer"
    role: "Review code for quality and best practices"

hooks:
  - name: "pre-commit"
    command: "promptrek validate"
```

**Key Features**:
- Markdown-first content approach
- Metadata for tracking and versioning
- Variable substitution support
- Plugin configuration (MCP servers, commands, agents, hooks)
- Multi-document support

### 2. Parser System

The parser converts YAML files into Python data models.

**Components**:

```python
# src/promptrek/core/parser.py
class UPFParser:
    def parse_file(self, file_path: Path) -> Union[
        UniversalPrompt,      # v1.0.0
        UniversalPromptV2,    # v2.x
        UniversalPromptV3     # v3.0.0
    ]:
        """Parse UPF file and return appropriate model."""
        # 1. Load YAML
        # 2. Detect schema version
        # 3. Validate basic structure
        # 4. Create appropriate model
        # 5. Return parsed prompt
```

**Data Models**:

```python
# src/promptrek/core/models.py
class UniversalPromptV3(BaseModel):
    schema_version: str = "3.0.0"
    metadata: PromptMetadata
    content: str
    documents: list[Document] | None = None
    variables: dict[str, str] | None = None
    mcp_servers: list[MCPServer] | None = None
    commands: list[Command] | None = None
    agents: list[Agent] | None = None
    hooks: list[Hook] | None = None
```

Uses Pydantic for validation and type safety.

### 3. Validator System

Ensures UPF files are correct before generation.

**Validation Layers**:

1. **Schema Validation**: Checks structure matches schema version
2. **Semantic Validation**: Verifies logical consistency
3. **Variable Validation**: Checks variable definitions and usage
4. **Plugin Validation**: Validates plugin configurations

```python
# src/promptrek/core/validator.py
class UPFValidator:
    def validate(self, prompt) -> ValidationResult:
        """Validate universal prompt."""
        result = ValidationResult()

        # Schema validation
        self._validate_schema(prompt, result)

        # Metadata validation
        self._validate_metadata(prompt.metadata, result)

        # Content validation
        self._validate_content(prompt, result)

        # Variable validation
        self._validate_variables(prompt, result)

        # Plugin validation (v2.1+/v3+)
        if hasattr(prompt, 'mcp_servers'):
            self._validate_plugins(prompt, result)

        return result
```

### 4. Adapter System

Adapters convert UPF to editor-specific formats using the adapter pattern.

**Base Adapter Interface**:

```python
# src/promptrek/adapters/base.py
class EditorAdapter(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: dict[str, str] | None = None,
    ) -> None:
        """Generate editor-specific files."""
        pass

    def supports_bidirectional_sync(self) -> bool:
        """Whether adapter supports syncing from editor files."""
        return False

    def parse_files(self, source_dir: Path) -> UniversalPromptV3:
        """Parse editor files back to UPF."""
        raise NotImplementedError("Sync not supported")
```

**Adapter Registry**:

```python
# src/promptrek/adapters/registry.py
class AdapterRegistry:
    _adapters: dict[str, Type[EditorAdapter]] = {}

    def register(self, name: str, adapter_class: Type[EditorAdapter]):
        """Register an adapter."""
        self._adapters[name] = adapter_class

    def get(self, name: str) -> EditorAdapter:
        """Get adapter instance."""
        if name not in self._adapters:
            raise AdapterNotFoundError(f"Adapter '{name}' not found")
        return self._adapters[name]()
```

**Registered Adapters**:
- `ClaudeAdapter` - Claude Code editor
- `ContinueAdapter` - Continue VSCode extension
- `CursorAdapter` - Cursor IDE
- `ClineAdapter` - Cline extension
- `WindsurfAdapter` - Windsurf IDE
- `AmazonQAdapter` - Amazon Q Developer
- `KiroAdapter` - Kiro editor
- And more...

### 5. Variable Substitution System

Handles variable resolution with precedence rules.

**Variable Types**:

1. **Built-in Variables** (lowest precedence):
```python
class BuiltInVariables:
    @staticmethod
    def get_all() -> dict[str, str]:
        return {
            "CURRENT_DATE": datetime.now().strftime("%Y-%m-%d"),
            "CURRENT_YEAR": datetime.now().strftime("%Y"),
            "CURRENT_MONTH": datetime.now().strftime("%B"),
            "CURRENT_TIME": datetime.now().strftime("%H:%M:%S"),
            "CURRENT_DATETIME": datetime.now().isoformat(),
        }
```

2. **Local Variables** (from `.promptrek/variables.promptrek.yaml`)
3. **Prompt Variables** (from `variables:` section)
4. **CLI Variables** (highest precedence, from `-V` flags)

**Substitution Process**:

```python
# src/promptrek/utils/variables.py
class VariableSubstitution:
    def substitute(self, content: str, variables: dict[str, str]) -> str:
        """Replace {{VAR}} with values."""
        for key, value in variables.items():
            pattern = f"{{{{{key}}}}}"  # {{KEY}}
            content = content.replace(pattern, value)
        return content
```

### 6. Template System (Optional)

Some adapters use Jinja2 templates for complex generation:

```
src/promptrek/templates/
├── claude/
│   └── prompt.md.j2
├── cursor/
│   └── cursorrules.j2
└── continue/
    ├── config.json.j2
    └── prompt.md.j2
```

**Template Example**:
```jinja2
{# templates/claude/prompt.md.j2 #}
# {{ metadata.title }}

{{ content }}

{% if variables %}
## Configuration Variables
{% for key, value in variables.items() %}
- {{ key }}: {{ value }}
{% endfor %}
{% endif %}
```

### 7. CLI System

Click-based command-line interface with commands and options.

**Structure**:

```python
# src/promptrek/cli/main.py
@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True)
@click.option("--interactive", "-i", is_flag=True)
@click.pass_context
def cli(ctx, verbose, interactive):
    """PrompTrek CLI."""
    if ctx.invoked_subcommand is None or interactive:
        run_interactive_mode(ctx)
```

**Commands**:
- `init` - Initialize new configuration
- `generate` - Generate editor files
- `validate` - Validate configuration
- `sync` - Sync from editor files
- `migrate` - Migrate schema versions
- `plugins` - Manage plugins
- `list-editors` - List supported editors
- `install-hooks` - Install pre-commit hooks
- `config-ignores` - Configure .gitignore

## Data Flow

### Generation Flow

```
1. Input: User runs `promptrek generate --editor claude`
   │
2. Parse: UPFParser reads and validates YAML
   │
3. Variable Resolution: Merge variables with precedence
   │
4. Adapter Selection: Get ClaudeAdapter from registry
   │
5. Generation: ClaudeAdapter.generate() creates files
   │
6. Output: Editor-specific files written to disk
   │
7. Metadata: Save generation metadata for refresh
```

### Sync Flow (Bidirectional)

```
1. Input: User runs `promptrek sync --editor continue`
   │
2. Adapter Selection: Get ContinueAdapter from registry
   │
3. Parse Editor Files: ContinueAdapter.parse_files()
   │
4. Merge: Combine with existing UPF (if present)
   │
5. Variable Restoration: Restore {{VAR}} references
   │
6. Output: Updated project.promptrek.yaml
```

### Validation Flow

```
1. Input: User runs `promptrek validate config.yaml`
   │
2. Parse: UPFParser reads YAML
   │
3. Schema Validation: Check structure matches schema
   │
4. Semantic Validation: Check logical consistency
   │
5. Variable Validation: Check variable definitions/usage
   │
6. Plugin Validation: Validate plugin configurations
   │
7. Output: Errors, warnings, or success
```

## File Organization

### Generated Files Structure

```
project-root/
├── project.promptrek.yaml         # Universal configuration
├── .promptrek/                    # User-specific config (gitignored)
│   ├── variables.promptrek.yaml   # Local variables
│   ├── last-generation.yaml       # Generation metadata
│   └── cache/                     # Template cache
├── .claude/                       # Claude configuration
│   ├── prompts/
│   │   └── project.md
│   └── config.json
├── .cursorrules                   # Cursor rules
├── .continue/                     # Continue configuration
│   ├── config.json
│   ├── prompts/
│   │   └── *.md
│   └── rules/
│       └── *.md
└── .cline/                        # Cline configuration
    └── prompts/
        └── *.md
```

## Security Considerations

### Template Injection Prevention

- Sandboxed Jinja2 environment
- No arbitrary code execution in templates
- Variable values sanitized before substitution

### Path Traversal Protection

```python
def validate_output_path(output_dir: Path, file_path: Path) -> bool:
    """Ensure file_path is within output_dir."""
    try:
        file_path.resolve().relative_to(output_dir.resolve())
        return True
    except ValueError:
        return False
```

### File Permission Handling

Generated files use safe permissions:
- Configuration files: 0644 (rw-r--r--)
- Directories: 0755 (rwxr-xr-x)

## Extensibility

### Adding New Editor Support

1. Create adapter class in `src/promptrek/adapters/myeditor.py`
2. Implement `EditorAdapter` interface
3. Register in `src/promptrek/adapters/registry.py`
4. Add tests in `tests/unit/adapters/test_myeditor.py`
5. Update documentation

### Adding New Schema Fields

1. Update models in `src/promptrek/core/models.py`
2. Update parser in `src/promptrek/core/parser.py`
3. Update validator in `src/promptrek/core/validator.py`
4. Update adapters to use new fields
5. Add migration support in `src/promptrek/cli/commands/migrate.py`
6. Update documentation and schema version

### Plugin System

v3.0.0 supports extensible plugins:
- **MCP Servers**: Model Context Protocol servers
- **Commands**: Slash commands for editors
- **Agents**: Autonomous agent configurations
- **Hooks**: Pre/post processing hooks

## Performance Considerations

### Caching

- Template compilation cached in `.promptrek/cache/`
- Variable evaluation cached during generation
- Cleared on schema changes

### Lazy Loading

- Adapters loaded only when needed
- Templates loaded on first use
- Large files streamed rather than loaded entirely

### Optimization Strategies

- Batch file operations when possible
- Parallel adapter execution for `--all` flag
- Minimal memory footprint for large configurations

## Error Handling Strategy

### Exception Hierarchy

```python
class PrompTrekError(Exception):
    """Base exception for PrompTrek."""

class UPFParsingError(PrompTrekError):
    """Error parsing UPF file."""

class ValidationError(PrompTrekError):
    """Validation failed."""

class AdapterNotFoundError(PrompTrekError):
    """Adapter not found in registry."""

class GenerationError(PrompTrekError):
    """Error during generation."""

class CLIError(PrompTrekError):
    """CLI-specific error."""
```

### Error Recovery

- Graceful degradation for non-critical errors
- Clear error messages with suggestions
- Rollback on generation failures

## Testing Architecture

### Test Structure

```
tests/
├── unit/                          # Unit tests
│   ├── test_parser.py             # Parser tests
│   ├── test_validator.py          # Validator tests
│   └── adapters/                  # Adapter tests
│       ├── test_claude.py
│       └── test_continue.py
├── integration/                   # Integration tests
│   ├── test_full_workflow.py
│   └── test_cli_integration.py
└── fixtures/                      # Test data
    ├── valid_prompts/
    ├── invalid_prompts/
    └── expected_outputs/
```

### Test Coverage Goals

- Overall: 90%+
- Core modules: 95%+
- Adapters: 85%+
- CLI: 80%+

## See Also

- [Project Structure](project-structure.md) - Detailed file organization
- [Contributing Guide](contributing.md) - Development workflow
- [UPF Specification](../user-guide/upf-specification.md) - Schema documentation
