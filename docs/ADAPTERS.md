# Editor Adapters

Agent Prompt Mapper supports multiple AI-powered code editors and assistants. Each adapter generates editor-specific configuration files optimized for that particular tool.

## Supported Editors

### ✅ Claude Code
**Generated Files**: `.claude/context.md`  
**Features**: Variable substitution, Conditional instructions

Claude Code adapter generates comprehensive context files in Markdown format that provide detailed project information and coding guidelines optimized for Claude's understanding.

**Example Output**:
```markdown
# My Project

## Project Overview
A modern web application built with React and TypeScript.

## Project Details
**Project Type:** web_application
**Technologies:** typescript, react, vite

## Development Guidelines
### General Principles
- Write clean, maintainable code
- Follow TypeScript best practices

### Code Style Requirements
- Use consistent indentation
- Prefer const over let

## Code Examples
### Component Example
const Button = ({ label }: { label: string }) => <button>{label}</button>;

## AI Assistant Instructions
When working on this project:
- Follow the established patterns and conventions shown above
- Maintain consistency with the existing codebase
- Consider the project context and requirements in all suggestions
```

### ✅ Continue
**Generated Files**: `.continue/config.json`  
**Features**: Variable substitution, Conditional instructions

Continue adapter generates JSON configuration files that integrate with Continue's VS Code extension for AI-powered code completion and chat.

**Example Output**:
```json
{
  "models": [],
  "systemMessage": "My Project\n\nA modern web application\n\nGeneral Instructions:\n- Write clean code\n- Follow best practices\n",
  "completionOptions": {},
  "allowAnonymousTelemetry": false
}
```

### ✅ Cline (Terminal-based AI)
**Generated Files**: `.cline/config.json`, `cline-context.md`  
**Features**: Variable substitution, Conditional instructions

Cline adapter generates both configuration and context files for terminal-based AI assistance, including safety settings and project context.

**Configuration Example**:
```json
{
  "name": "My Project",
  "description": "Project description",
  "contextFile": "cline-context.md",
  "settings": {
    "autoSuggest": true,
    "verboseLogging": false,
    "safeMode": true
  },
  "project": {
    "type": "web_application",
    "technologies": ["typescript", "react"]
  }
}
```

### ✅ Codeium
**Generated Files**: `.codeium/context.json`, `.codeiumrc`  
**Features**: Variable substitution, Conditional instructions

Codeium adapter generates structured JSON context files and RC configuration files that integrate with Codeium's AI code assistance.

**Context JSON Example**:
```json
{
  "project": {
    "name": "My Project",
    "technologies": ["typescript", "react"],
    "type": "web_application"
  },
  "guidelines": [
    {"category": "general", "rule": "Write clean code"},
    {"category": "style", "rule": "Use consistent indentation"}
  ],
  "patterns": [
    {
      "name": "component",
      "description": "Example component",
      "example": "const Button = ..."
    }
  ],
  "preferences": {
    "style": "consistent",
    "verbosity": "medium",
    "languages": ["typescript", "react"]
  }
}
```

### ✅ GitHub Copilot
**Generated Files**: `.github/copilot-instructions.md`  
**Features**: Variable substitution, Conditional instructions

Generates GitHub Copilot instruction files that provide context and guidelines for AI-assisted development.

### ✅ Cursor
**Generated Files**: `.cursorrules`  
**Features**: Variable substitution, Conditional instructions

Generates Cursor rules files that configure the Cursor AI editor with project-specific instructions and guidelines.

## Using Adapters

### Generate for Single Editor
```bash
apm generate --editor claude --output ./output project.apm.yaml
```

### Generate for All Target Editors
```bash
apm generate --all --output ./output project.apm.yaml
```

### Dry Run (Preview Mode)
```bash
apm generate --editor claude --output ./output --dry-run project.apm.yaml
```

### With Variable Overrides
```bash
apm generate --editor claude --output ./output project.amp.yaml \
  -V PROJECT_NAME="CustomProject" \
  -V AUTHOR="Custom Author"
```

## Editor-Specific Features

### Conditional Instructions

Different editors have different strengths. Use conditionals to provide editor-specific guidance:

```yaml
conditions:
  - if: "EDITOR == \"claude\""
    then:
      instructions:
        general:
          - "Provide detailed explanations for complex logic"
          - "Focus on code clarity and readability"

  - if: "EDITOR == \"continue\""
    then:
      instructions:
        general:
          - "Generate comprehensive code completions"
          - "Suggest appropriate TypeScript types"

  - if: "EDITOR in [\"codeium\", \"cursor\"]"
    then:
      instructions:
        general:
          - "Focus on performance optimization"
          - "Suggest modern React patterns"
```

### Variable Substitution in Editor Content

All adapters support variable substitution in their generated content:

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

## Adapter Architecture

### Built-in Capabilities

All adapters inherit these capabilities from the base adapter:

- **Variable Substitution**: Replace template variables with actual values
- **Conditional Processing**: Apply different instructions based on conditions
- **Content Validation**: Validate prompt structure for editor compatibility
- **File Generation**: Create editor-specific files with appropriate structure

### Editor-Specific Optimizations

Each adapter optimizes content for its target editor:

- **Claude**: Emphasizes detailed context and examples for better understanding
- **Continue**: Focuses on system messages and completion hints
- **Cline**: Includes safety settings and terminal-specific guidance
- **Codeium**: Structures content for AI code assistance patterns
- **Copilot**: Uses GitHub's instruction format and conventions
- **Cursor**: Follows Cursor's rules file format

## Adding New Adapters

To add support for new AI editors:

1. Create a new adapter class inheriting from `EditorAdapter`
2. Implement required methods: `generate()`, `validate()`
3. Define editor-specific file patterns and content builders  
4. Register the adapter in the adapter registry
5. Add tests for the new adapter

Example adapter structure:

```python
class NewEditorAdapter(EditorAdapter):
    def __init__(self):
        super().__init__(
            name="neweditor",
            description="New Editor (config-based)",
            file_patterns=[".neweditor/config.json"]
        )
    
    def generate(self, prompt, output_dir, dry_run=False, verbose=False, variables=None):
        # Apply variable substitution and conditionals
        processed_prompt = self.substitute_variables(prompt, variables)
        conditional_content = self.process_conditionals(processed_prompt, variables)
        
        # Generate editor-specific content
        content = self._build_content(processed_prompt, conditional_content)
        
        # Create output file
        # ... implementation
    
    def validate(self, prompt):
        # Editor-specific validation
        # ... implementation
    
    def supports_variables(self):
        return True
    
    def supports_conditionals(self):
        return True
```

## Best Practices

### Universal Instructions
- Write instructions that work well across all editors
- Use editor-specific conditionals sparingly
- Focus on code quality and project-specific guidance

### Editor Selection
- Choose editors based on your development workflow
- Consider team preferences and tool availability
- Test generated configurations with actual editor installations

### File Organization
Generated files are organized by editor:

```
project/
├── .claude/
│   └── context.md
├── .continue/
│   └── config.json
├── .codeium/
│   ├── context.json
│   └── .codeiumrc
├── .github/
│   └── copilot-instructions.md
├── .cursorrules
└── cline-context.md
```

### Version Control
Add generated files to `.gitignore` if they contain sensitive information or are environment-specific:

```gitignore
# Generated AI configuration files
.claude/
.continue/
.codeium/
.codeiumrc
cline-context.md

# Keep these if they're project-wide
# .github/copilot-instructions.md
# .cursorrules
```

## Troubleshooting

### Common Issues

**Missing Editor Support**: Check that the editor is in your `targets` list:
```bash
Error: Editor 'claude' not in targets: copilot, cursor
```

**File Generation Errors**: Ensure output directory exists and is writable:
```bash
apm generate --editor claude --output ./output project.apm.yaml
```

**Conditional Not Working**: Check condition syntax and variable names:
```yaml
# Correct
- if: "EDITOR == \"claude\""

# Incorrect  
- if: "EDITOR = \"claude\""  # Single = instead of ==
```

### Getting Help

- Use `apm list-editors` to see all supported editors
- Use `--dry-run` to preview generated content
- Use `--verbose` for detailed operation logs
- Check the generated files match your editor's expected format