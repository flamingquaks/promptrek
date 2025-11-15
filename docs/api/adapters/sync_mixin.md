# Sync Mixin

The sync mixin provides utilities for bidirectional synchronization - parsing editor-specific files back into Universal Prompt Format.

## Overview

PrompTrek provides two sync mixins for different file structures:

- **MarkdownSyncMixin**: For editors with multiple markdown files (Cursor, Copilot, Continue)
- **SingleFileMarkdownSyncMixin**: For editors with single markdown files (Claude)

These mixins enable:

- **Lossless bidirectional sync**: Parse editor files back to UPF without data loss
- **Frontmatter extraction**: Parse YAML frontmatter from markdown files
- **Document organization**: Handle multi-file configurations
- **Variable preservation**: Maintain variable placeholders during roundtrip
- **Metadata generation**: Auto-generate metadata when parsing

Adapters can inherit from these mixins to add sync capabilities.

## API Reference

::: promptrek.adapters.sync_mixin
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      docstring_style: google
      show_if_no_docstring: false

## Usage Examples

### Using MarkdownSyncMixin

Parse multiple markdown files into UPF v3:

```python
from pathlib import Path
from promptrek.adapters.sync_mixin import MarkdownSyncMixin

class CursorAdapter(MarkdownSyncMixin):
    """Cursor adapter with sync support."""

    def parse_files(self, source_dir: Path):
        """Parse Cursor rules back to UPF."""
        return self.parse_markdown_rules_files(
            source_dir=source_dir,
            rules_subdir=".cursor/rules",
            file_extension="mdc",
            editor_name="Cursor"
        )

# Use it
adapter = CursorAdapter()
prompt = adapter.parse_files(Path("."))

print(f"Parsed: {prompt.metadata.title}")
print(f"Schema: {prompt.schema_version}")
print(f"Documents: {len(prompt.documents) if prompt.documents else 0}")
```

### Using SingleFileMarkdownSyncMixin

Parse a single markdown file into UPF:

```python
from pathlib import Path
from promptrek.adapters.sync_mixin import SingleFileMarkdownSyncMixin

class ClaudeAdapter(SingleFileMarkdownSyncMixin):
    """Claude adapter with sync support."""

    def parse_files(self, source_dir: Path):
        """Parse CLAUDE.md back to UPF."""
        # Parse to v3 (lossless)
        return self.parse_single_markdown_file_v3(
            source_dir=source_dir,
            file_path=".claude/CLAUDE.md",
            editor_name="Claude Code"
        )

# Use it
adapter = ClaudeAdapter()
prompt = adapter.parse_files(Path("."))

print(f"Title: {prompt.metadata.title}")
print(f"Content length: {len(prompt.content)}")
```

### Parsing with Frontmatter

Parse markdown with YAML frontmatter:

```python
from pathlib import Path
from promptrek.adapters.sync_mixin import SingleFileMarkdownSyncMixin

# Markdown file content:
"""
---
title: "My Project Rules"
description: "Custom AI assistant configuration"
version: "2.1.0"
author: "John Doe"
tags: ["python", "api"]
---

# Development Guidelines

- Write clean code
- Add tests
- Document APIs
"""

mixin = SingleFileMarkdownSyncMixin()

# Create temporary file
md_path = Path("test.md")
md_path.write_text(content)

# Parse with frontmatter extraction
prompt = mixin.parse_single_markdown_file_v3(
    source_dir=Path("."),
    file_path="test.md",
    editor_name="Test"
)

# Frontmatter values are extracted to metadata
print(f"Title: {prompt.metadata.title}")  # "My Project Rules"
print(f"Version: {prompt.metadata.version}")  # "2.1.0"
print(f"Author: {prompt.metadata.author}")  # "John Doe"
print(f"Tags: {prompt.metadata.tags}")  # ["python", "api"]

# Content excludes frontmatter
print(f"Content starts with: {prompt.content[:20]}")  # "# Development Guidel..."
```

### Multi-Document Parsing

Parse multiple markdown files as documents:

```python
from pathlib import Path
from promptrek.adapters.sync_mixin import MarkdownSyncMixin

# Directory structure:
# .cursor/rules/
#   ├── index.mdc          # Main rules
#   ├── python-rules.mdc   # Python-specific
#   └── testing-rules.mdc  # Testing rules

mixin = MarkdownSyncMixin()

prompt = mixin.parse_markdown_rules_files(
    source_dir=Path("."),
    rules_subdir=".cursor/rules",
    file_extension="mdc",
    editor_name="Cursor"
)

# index.mdc becomes main content
print(f"Main content: {prompt.content[:50]}...")

# Other files become documents
if prompt.documents:
    print(f"\nDocuments: {len(prompt.documents)}")
    for doc in prompt.documents:
        print(f"  - {doc.name}")

# Example output:
# Main content: # General Development Rules...
#
# Documents: 2
#   - python-rules
#   - testing-rules
```

### Extracting Title from Markdown

Automatically extract title from first H1 heading:

```python
from promptrek.adapters.sync_mixin import SingleFileMarkdownSyncMixin

mixin = SingleFileMarkdownSyncMixin()

# Markdown with H1 heading
content = """
# Python API Development

Best practices for Python API development.

## Guidelines

- Use FastAPI
- Add type hints
"""

# Extract title
title = mixin._extract_title_from_markdown(content)
print(f"Extracted title: {title}")  # "Python API Development"

# No H1 heading
content_no_h1 = """
## Guidelines

- Use FastAPI
"""

title = mixin._extract_title_from_markdown(content_no_h1)
print(f"Title: {title}")  # None
```

### Extracting Frontmatter

Extract YAML frontmatter from markdown:

```python
from promptrek.adapters.sync_mixin import SingleFileMarkdownSyncMixin

mixin = SingleFileMarkdownSyncMixin()

content = """---
name: "python-rules"
description: "Python coding standards"
applyToFiles: "**/*.py"
alwaysApply: false
---

# Python Rules

- Use type hints
- Follow PEP 8
"""

frontmatter, remaining = mixin._extract_frontmatter(content)

print("Frontmatter:")
print(frontmatter)
# {'name': 'python-rules', 'description': 'Python coding standards',
#  'applyToFiles': '**/*.py', 'alwaysApply': False}

print("\nContent:")
print(remaining)
# "# Python Rules\n\n- Use type hints\n- Follow PEP 8"
```

### Document Configuration from Frontmatter

Create DocumentConfig with frontmatter metadata:

```python
from promptrek.adapters.sync_mixin import MarkdownSyncMixin
from promptrek.core.models import DocumentConfig

# File: .cursor/rules/python-rules.mdc
content = """---
name: "Python Standards"
description: "Python-specific coding standards"
applyToFiles: "**/*.py"
alwaysApply: false
---

# Python Development

- Use Python 3.11+
- Add type hints to all functions
- Use black for formatting
"""

mixin = MarkdownSyncMixin()

# Parse frontmatter
if content.startswith("---"):
    parts = content.split("---", 2)
    import yaml
    frontmatter = yaml.safe_load(parts[1])
    actual_content = parts[2].strip()

    # Create DocumentConfig with frontmatter fields
    doc = DocumentConfig(
        name=frontmatter.get("name", "python-rules"),
        content=actual_content,
        description=frontmatter.get("description"),
        file_globs=frontmatter.get("applyToFiles"),
        always_apply=frontmatter.get("alwaysApply")
    )

    print(f"Document: {doc.name}")
    print(f"Applies to: {doc.file_globs}")
    print(f"Always apply: {doc.always_apply}")
```

### Parsing to Different UPF Versions

Parse markdown to v1, v2, or v3:

```python
from pathlib import Path
from promptrek.adapters.sync_mixin import SingleFileMarkdownSyncMixin

mixin = SingleFileMarkdownSyncMixin()

# Parse to v1 (structured, lossy)
prompt_v1 = mixin.parse_single_markdown_file(
    source_dir=Path("."),
    file_path=".claude/CLAUDE.md",
    editor_name="Claude"
)
print(f"V1 schema: {prompt_v1.schema_version}")  # "1.0.0"

# Parse to v2 (markdown-first, lossless)
prompt_v2 = mixin.parse_single_markdown_file_v2(
    source_dir=Path("."),
    file_path=".claude/CLAUDE.md",
    editor_name="Claude"
)
print(f"V2 schema: {prompt_v2.schema_version}")  # "2.0.0"

# Parse to v3 (markdown-first with plugins, lossless)
prompt_v3 = mixin.parse_single_markdown_file_v3(
    source_dir=Path("."),
    file_path=".claude/CLAUDE.md",
    editor_name="Claude"
)
print(f"V3 schema: {prompt_v3.schema_version}")  # "3.1.0"
```

### Mapping Filenames to Categories (V1)

Map markdown filenames to instruction categories:

```python
from promptrek.adapters.sync_mixin import MarkdownSyncMixin

mixin = MarkdownSyncMixin()

# Test various filenames
filenames = [
    "general-rules",
    "code-style",
    "python-rules",
    "testing-guidelines",
    "security",
    "performance"
]

for filename in filenames:
    category = mixin._map_filename_to_category(filename)
    print(f"{filename} → {category}")

# Output:
# general-rules → general
# code-style → code_style
# python-rules → technology
# testing-guidelines → testing
# security → security
# performance → performance
```

### Extracting Technology Names

Extract technology from filename:

```python
from promptrek.adapters.sync_mixin import MarkdownSyncMixin

mixin = MarkdownSyncMixin()

filenames = [
    "python-rules",
    "typescript-guidelines",
    "react-guide",
]

for filename in filenames:
    tech = mixin._extract_technology_from_filename(filename)
    print(f"{filename} → {tech}")

# Output:
# python-rules → python
# typescript-guidelines → typescript
# react-guide → react
```

### Extracting Context from Content (V1)

Parse project context from markdown content:

```python
from promptrek.adapters.sync_mixin import SingleFileMarkdownSyncMixin

mixin = SingleFileMarkdownSyncMixin()

content = """
# My Project

Technologies: Python, FastAPI, PostgreSQL, React

This is a full-stack web application.
"""

context = mixin._extract_context_from_content(content)

if context:
    print(f"Project type: {context.project_type}")
    print(f"Technologies: {context.technologies}")
    print(f"Description: {context.description}")

# Output:
# Project type: application
# Technologies: ['Python', 'FastAPI', 'PostgreSQL', 'React']
# Description: Project using Python, FastAPI, PostgreSQL, React
```

### Parsing Markdown Sections (V1)

Parse structured sections from markdown:

```python
from promptrek.adapters.sync_mixin import SingleFileMarkdownSyncMixin

mixin = SingleFileMarkdownSyncMixin()

content = """
# Project Guidelines

## General

- Write clean code
- Use meaningful names
- Document your code

## Code Style

- Follow PEP 8 for Python
- Use ESLint for JavaScript
- Format with Prettier

## Testing

- Write unit tests
- Aim for >80% coverage
- Use pytest for Python
"""

instructions = mixin._parse_markdown_sections(content)

for category, items in instructions.items():
    print(f"\n{category}:")
    for item in items:
        print(f"  - {item}")

# Output:
# general:
#   - Write clean code
#   - Use meaningful names
#   - Document your code
#
# code_style:
#   - Follow PEP 8 for Python
#   - Use ESLint for JavaScript
#   - Format with Prettier
#
# testing:
#   - Write unit tests
#   - Aim for >80% coverage
#   - Use pytest for Python
```

### Complete Sync Example

Full bidirectional sync workflow:

```python
from pathlib import Path
from promptrek.core.parser import UPFParser
from promptrek.adapters.registry import registry
import yaml

# 1. Start with UPF file
parser = UPFParser()
original_prompt = parser.parse_file(".promptrek.yaml")

# 2. Generate editor files
adapter = registry.get("cursor")
files = adapter.generate(original_prompt, Path("."))
print(f"Generated: {files}")

# 3. Edit files manually in editor...
# (User modifies .cursor/rules/*.mdc files)

# 4. Sync back to UPF
synced_prompt = adapter.parse_files(Path("."))

# 5. Save as new UPF file
output_path = Path(".promptrek-synced.yaml")
with open(output_path, "w") as f:
    yaml.safe_dump(synced_prompt.model_dump(), f)

print(f"Synced back to: {output_path}")
print(f"Title: {synced_prompt.metadata.title}")
print(f"Documents: {len(synced_prompt.documents or [])}")
```

### Variable Preservation During Sync

Preserve variable placeholders when syncing:

```python
from pathlib import Path
from promptrek.utils.variables import VariableSubstitution
from promptrek.adapters.sync_mixin import SingleFileMarkdownSyncMixin

# Original content with variables
original = "Project: {{{ PROJECT_NAME }}}\nEnv: {{{ ENVIRONMENT }}}"

# Generated content (variables substituted)
generated = "Project: my-awesome-app\nEnv: production"

# During sync, restore variables
var_sub = VariableSubstitution()
restored = var_sub.restore_variables_in_content(
    original_content=original,
    parsed_content=generated,
    verbose=True
)

print(restored)
# Output: "Project: {{{ PROJECT_NAME }}}\nEnv: {{{ ENVIRONMENT }}}"
```

### Error Handling

Handle sync errors gracefully:

```python
from pathlib import Path
from promptrek.adapters.sync_mixin import MarkdownSyncMixin

mixin = MarkdownSyncMixin()

try:
    prompt = mixin.parse_markdown_rules_files(
        source_dir=Path("."),
        rules_subdir=".nonexistent/rules",
        file_extension="md",
        editor_name="Test"
    )

    # If directory doesn't exist, returns prompt with default content
    print(f"Content: {prompt.content}")
    # Output: "# Test\n\nNo rules found."

except Exception as e:
    print(f"Sync error: {e}")
```

## Sync Workflow Patterns

### Pattern 1: Lossless V3 Sync

Use v3 for lossless bidirectional sync:

```python
# Generate: UPF v3 → Markdown
adapter.generate(upf_v3_prompt, output_dir)

# Edit markdown files in editor...

# Sync: Markdown → UPF v3 (lossless)
synced_prompt = adapter.parse_files(output_dir)

# synced_prompt preserves all original content
```

### Pattern 2: Structured V1 Conversion

Convert markdown to structured v1:

```python
# Parse markdown to v1 (lossy but structured)
v1_prompt = adapter.parse_single_markdown_file(
    source_dir,
    file_path,
    editor_name
)

# Access structured data
if v1_prompt.instructions:
    print(v1_prompt.instructions.general)
    print(v1_prompt.instructions.code_style)
```

## See Also

- [Base Adapter](base.md) - Adapter interface
- [Variables Module](../utils/variables.md) - Variable restoration
- [Sync Command](../../cli/sync.md) - CLI sync functionality
- [Bidirectional Sync Guide](../../user-guide/bidirectional-sync.md) - Sync workflows
