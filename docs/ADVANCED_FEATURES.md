# Advanced Template Features

PrompTrek supports powerful advanced template features that allow you to create flexible, maintainable prompt configurations.

## Variable Substitution

Variables allow you to create reusable templates that can be customized for different projects or contexts.

### Basic Variable Syntax

Use triple braces to define variable placeholders in your UPF files:

```yaml
metadata:
  title: "{{{ PROJECT_NAME }}} Assistant"
  description: "AI assistant for {{{ PROJECT_NAME }}}"

instructions:
  general:
    - "Follow {{{ PROJECT_NAME }}} coding standards"
    - "Contact {{{ AUTHOR_EMAIL }}} for questions"

variables:
  PROJECT_NAME: "MyProject" 
  AUTHOR_EMAIL: "team@example.com"
```

### Environment Variables

You can also reference environment variables using `${}` syntax:

```yaml
metadata:
  author: "${AUTHOR_NAME}"
  
instructions:
  general:
    - "Deploy to ${ENVIRONMENT} environment"
```

### Local Variables File

PrompTrek supports a `variables.promptrek.yaml` file for user-specific variables that should not be committed to version control. This is perfect for storing local paths, API keys, personal information, or any variable that varies between team members.

**Creating a local variables file:**

```yaml
# variables.promptrek.yaml
# This file contains local variables that should NOT be committed
# Add this file to .gitignore

# User-specific variables
AUTHOR_NAME: "Your Name"
AUTHOR_EMAIL: "your.email@example.com"
API_KEY: "your-api-key-here"
LOCAL_PATH: "/path/to/local/resource"
ENVIRONMENT: "development"
```

**How it works:**

1. When you run `promptrek init`, it automatically adds `variables.promptrek.yaml` to your `.gitignore`
2. Create your local variables file manually with user-specific values
3. PrompTrek automatically loads variables from this file when generating
4. Pre-commit hooks prevent accidental commits of this file

**Variable Precedence (highest to lowest):**

1. CLI overrides (`-V KEY=value`)
2. Local variables file (`variables.promptrek.yaml`)
3. Prompt file variables section

**Example usage:**

```yaml
# project.promptrek.yaml (committed to git)
metadata:
  title: "{{{ PROJECT_NAME }}} Assistant"
  author: "{{{ AUTHOR_NAME }}}"

variables:
  PROJECT_NAME: "MyProject"
  AUTHOR_NAME: "Team"  # Default fallback
```

```yaml
# variables.promptrek.yaml (local, in .gitignore)
AUTHOR_NAME: "John Doe"
AUTHOR_EMAIL: "john@example.com"
```

When generating, `AUTHOR_NAME` will be "John Doe" from the local file, overriding the default in the prompt file.

### CLI Variable Overrides

Override variables from the command line using `-V` or `--var`:

```bash
promptrek generate --editor claude --output ./output project.promptrek.yaml \
  -V PROJECT_NAME="CustomProject" \
  -V AUTHOR_EMAIL="custom@example.com"
```

CLI overrides have the highest precedence and will override both local variables and prompt file variables.

## Conditional Instructions

Conditional instructions allow you to provide different instructions based on the target editor or other conditions.

### Basic Conditionals

```yaml
conditions:
  - if: "EDITOR == \"claude\""
    then:
      instructions:
        general:
          - "Claude-specific: Provide detailed explanations"
          - "Claude-specific: Focus on code clarity"
      examples:
        claude_example: "// Example optimized for Claude"

  - if: "EDITOR == \"continue\""
    then:
      instructions:
        general:
          - "Continue-specific: Generate comprehensive completions"
```

### Supported Conditions

- **Equality**: `EDITOR == "claude"`
- **Inequality**: `EDITOR != "copilot"`  
- **List membership**: `EDITOR in ["claude", "cursor"]`
- **Boolean variables**: `DEBUG_MODE` (checks if variable is truthy)

### Conditional Examples and Variables

Conditionals can modify any part of your configuration:

```yaml
conditions:
  - if: "PROJECT_TYPE == \"mobile\""
    then:
      examples:
        mobile_component: "const Screen = () => <View><Text>Hello</Text></View>;"
      variables:
        PLATFORM: "React Native"

  - if: "ENVIRONMENT == \"production\""
    then:
      instructions:
        general:
          - "Use production-safe coding practices"
          - "Include comprehensive error handling"
```

## Import System

The import system allows you to share common configurations across multiple projects.

### Basic Import

Create a base configuration file:

```yaml
# base-config.promptrek.yaml
schema_version: "1.0.0"

metadata:
  title: "Base Configuration"
  description: "Shared configuration"
  version: "1.0.0"
  author: "team@company.com"
  created: "2024-01-01"
  updated: "2024-01-01"

targets:
  - claude

instructions:
  general:
    - "Follow clean code principles"
    - "Use meaningful variable names"
  code_style:
    - "Use 2-space indentation"
    - "Prefer const over let"

examples:
  util_function: "const capitalize = (str) => str.charAt(0).toUpperCase() + str.slice(1);"

variables:
  STYLE_GUIDE: "Company Standard"
  INDENT_SIZE: "2"
```

Then import it in your main file:

```yaml
# project.promptrek.yaml
schema_version: "1.0.0"

metadata:
  title: "My Project"
  description: "Project with shared configuration"
  # ... other metadata

targets:
  - claude

imports:
  - path: "base-config.promptrek.yaml"
    prefix: "shared"

instructions:
  general:
    - "Project-specific instruction"
  testing:
    - "Write comprehensive tests"
```

### Import with Prefix

The `prefix` option namespaces imported content to avoid conflicts:

- Instructions get prefixed: `[shared] Follow clean code principles`
- Examples get prefixed: `shared_util_function`  
- Variables get prefixed: `shared_STYLE_GUIDE`

### Import Behavior

- **Instructions**: Imported instructions are merged with existing ones
- **Examples**: Imported examples are added with prefixed names
- **Variables**: Imported variables are added with prefixed names (unless already present)
- **Metadata**: Metadata from imported files is ignored (only the main file's metadata is used)

### Relative Paths

Import paths are relative to the importing file:

```
project/
├── config/
│   └── base.promptrek.yaml
├── frontend/
│   └── frontend.promptrek.yaml  # imports: path: "../config/base.promptrek.yaml"
└── backend/
    └── backend.promptrek.yaml   # imports: path: "../config/base.promptrek.yaml"
```

### Circular Import Protection

The import system automatically detects and prevents circular imports:

```yaml
# file-a.promptrek.yaml
imports:
  - path: "file-b.promptrek.yaml"

# file-b.promptrek.yaml  
imports:
  - path: "file-a.promptrek.yaml"  # This will cause an error
```

## Combining Features

All advanced features work together seamlessly:

```yaml
# base.promptrek.yaml
instructions:
  general:
    - "Use {{{ CODING_STYLE }}} coding style"

conditions:
  - if: "EDITOR == \"claude\""
    then:
      instructions:
        general:
          - "Claude: Use {{{ AI_APPROACH }}} approach"

variables:
  CODING_STYLE: "clean"
  AI_APPROACH: "detailed"

# main.promptrek.yaml
imports:
  - path: "base.promptrek.yaml"
    prefix: "base"

conditions:
  - if: "EDITOR == \"claude\""
    then:
      instructions:
        general:
          - "Main: Use {{{ MAIN_APPROACH }}} methodology"

variables:
  PROJECT_NAME: "AdvancedProject"
  MAIN_APPROACH: "comprehensive"
```

Generate with overrides:

```bash
promptrek generate --editor claude --output ./output main.promptrek.yaml \
  -V PROJECT_NAME="CustomProject" \
  -V base_CODING_STYLE="strict" \
  -V base_AI_APPROACH="concise"
```

This will:
1. Import base configuration with "base" prefix
2. Apply variable substitution to both files
3. Process conditionals for Claude editor
4. Override variables via CLI
5. Merge all instructions and content

## Best Practices

### Variables
- Use UPPER_CASE for variable names
- Provide sensible defaults in the `variables` section
- Use descriptive variable names: `PROJECT_NAME` not `PN`

### Conditionals  
- Keep conditions simple and readable
- Use editor-specific instructions sparingly - most instructions should be universal
- Test your conditionals with different editors

### Imports
- Use prefixes to avoid naming conflicts
- Keep shared configurations focused and minimal
- Document your import structure in README files
- Use relative paths for portability

### Organization
```
project/
├── shared/
│   ├── base-coding-standards.promptrek.yaml
│   ├── base-testing.promptrek.yaml
│   └── base-typescript.promptrek.yaml
├── frontend/
│   └── frontend.promptrek.yaml
├── backend/  
│   └── backend.promptrek.yaml
└── README.md  # Document your configuration structure
```
