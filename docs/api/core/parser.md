# Parser Module

The parser module provides functionality for loading and parsing Universal Prompt Format (UPF) files into structured Python objects.

## Overview

The `UPFParser` class is the main entry point for parsing `.promptrek.yaml` files. It handles:

- **Multi-version support**: Automatically detects and parses v1.x, v2.x, and v3.x UPF files
- **File and string parsing**: Parse from files on disk or YAML strings
- **Validation**: Built-in schema validation using Pydantic models
- **Import resolution**: Processes `imports` field to merge multiple UPF files (v1 only)
- **Backward compatibility**: Handles deprecated v3.0 nested plugin structures
- **Batch processing**: Find and parse multiple UPF files from directories

The parser uses Pydantic for robust schema validation and provides helpful error messages when parsing fails.

## API Reference

::: promptrek.core.parser
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      docstring_style: google
      show_if_no_docstring: false

## Usage Examples

### Basic File Parsing

Parse a single UPF file from disk:

```python
from promptrek.core.parser import UPFParser
from pathlib import Path

# Initialize parser
parser = UPFParser()

# Parse a UPF file
prompt = parser.parse_file(".promptrek.yaml")

# Access metadata
print(f"Title: {prompt.metadata.title}")
print(f"Version: {prompt.schema_version}")
print(f"Description: {prompt.metadata.description}")
```

### Version Detection

The parser automatically detects the schema version:

```python
from promptrek.core.parser import UPFParser

parser = UPFParser()

# Parser returns different types based on schema_version
prompt = parser.parse_file("config.promptrek.yaml")

# Check which version was parsed
if hasattr(prompt, 'content'):
    print(f"Parsed as v2/v3 (markdown-first)")
    print(f"Content preview: {prompt.content[:100]}...")
else:
    print(f"Parsed as v1 (structured)")
    if prompt.instructions:
        print(f"General instructions: {len(prompt.instructions.general or [])}")
```

### Parsing from String

Parse YAML content directly from a string:

```python
from promptrek.core.parser import UPFParser

yaml_content = """
schema_version: "3.0.0"
metadata:
  title: "My Project Rules"
  description: "AI coding assistant rules"
content: |
  # Project Guidelines

  - Write clean, maintainable code
  - Include comprehensive tests
  - Document all public APIs
"""

parser = UPFParser()
prompt = parser.parse_string(yaml_content, source="<example>")

print(f"Parsed: {prompt.metadata.title}")
print(f"Content length: {len(prompt.content)}")
```

### Finding UPF Files

Discover all UPF files in a directory:

```python
from promptrek.core.parser import UPFParser
from pathlib import Path

parser = UPFParser()

# Find all .promptrek.yaml files (non-recursive)
upf_files = parser.find_upf_files(Path.cwd(), recursive=False)
print(f"Found {len(upf_files)} UPF files")

# Find recursively
all_files = parser.find_upf_files(Path.cwd(), recursive=True)
for file in all_files:
    print(f"  - {file}")
```

### Parsing Multiple Files

Parse and merge multiple UPF files:

```python
from promptrek.core.parser import UPFParser
from pathlib import Path

parser = UPFParser()

# Parse multiple files and merge them
files = [
    Path("base.promptrek.yaml"),
    Path("python.promptrek.yaml"),
    Path("testing.promptrek.yaml")
]

merged_prompt = parser.parse_multiple_files(files)
print(f"Merged prompt: {merged_prompt.metadata.title}")
```

### Parsing an Entire Directory

Parse all UPF files in a directory and merge them:

```python
from promptrek.core.parser import UPFParser
from pathlib import Path

parser = UPFParser()

# Parse all files in a directory
try:
    merged = parser.parse_directory(Path(".promptrek"), recursive=True)
    print(f"Successfully merged {merged.metadata.title}")
except Exception as e:
    print(f"Error: {e}")
```

### Error Handling

The parser raises specific exceptions for different error conditions:

```python
from promptrek.core.parser import UPFParser
from promptrek.core.exceptions import (
    UPFFileNotFoundError,
    UPFParsingError
)

parser = UPFParser()

try:
    prompt = parser.parse_file("nonexistent.yaml")
except UPFFileNotFoundError as e:
    print(f"File not found: {e}")
except UPFParsingError as e:
    print(f"Parsing error: {e}")
```

### Working with V3 Backward Compatibility

The parser automatically handles deprecated v3.0 nested plugin structures:

```python
from promptrek.core.parser import UPFParser

# This YAML uses the old v3.0 nested structure:
yaml_v3_old = """
schema_version: "3.0.0"
metadata:
  title: "Old V3 Format"
  description: "Uses nested plugins"
content: "# My Rules"
plugins:
  mcp_servers:
    - name: "filesystem"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-filesystem"]
"""

parser = UPFParser()

# Parser auto-promotes to top-level (with deprecation warning)
prompt = parser.parse_string(yaml_v3_old)

# Fields are now at top level
if prompt.mcp_servers:
    print(f"MCP servers: {len(prompt.mcp_servers)}")
```

### Validating File Extensions

Check if a file has a valid UPF extension:

```python
from promptrek.core.parser import UPFParser
from pathlib import Path

parser = UPFParser()

# Check various files
files = [
    ".promptrek.yaml",      # Valid
    ".promptrek.yml",       # Valid
    "config.yaml",          # Invalid
    "rules.md"              # Invalid
]

for file in files:
    is_valid = parser.validate_file_extension(Path(file))
    print(f"{file}: {'✓' if is_valid else '✗'}")
```

## Error Messages

The parser provides detailed error messages to help diagnose issues:

### Schema Validation Errors

```
Validation errors in .promptrek.yaml:
  metadata -> title: field required
  content: Content cannot be empty
  schema_version: Schema version must be in format 'x.y.z'
```

### YAML Parsing Errors

```
YAML parsing error in config.promptrek.yaml:
  mapping values are not allowed here
  in "<unicode string>", line 5, column 15
```

### File Not Found Errors

```
UPF file not found: /path/to/missing.promptrek.yaml
```

## See Also

- [Validator Module](validator.md) - Validate parsed UPF objects
- [Models Module](models.md) - UPF data model definitions
- [Exceptions Module](exceptions.md) - Exception types
- [UPF Schema Reference](../../schema/index.md) - Complete schema documentation
