---
layout: default
title: Architecture
---

# System Architecture

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Universal      │    │   CLI Tool      │    │ Editor-Specific │
│  Prompt Files   │───▶│  (Mapper)       │───▶│ Prompt Files    │
│  (.promptrek.yaml)    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Configuration  │
                       │  & Templates    │
                       └─────────────────┘
```

## Core Components

### 1. Universal Prompt Format (UPF)

**Purpose**: Standardized format for storing prompts that can be converted to any editor format

**File Extension**: `.promptrek.yaml` (PrompTrek)

**Structure**:
```yaml
metadata:
  title: "Project Assistant Configuration"
  description: "Instructions for AI assistants working on this project"
  version: "1.0.0"
  author: "Developer Name"
  created: "2024-01-01"
  updated: "2024-01-15"

targets:
  - copilot
  - cursor
  - continue

context:
  project_type: "web_application"
  technologies:
    - "typescript"
    - "react"
    - "node.js"
  description: |
    This is a modern web application built with React and TypeScript.
    It follows clean architecture principles and uses functional programming patterns.

instructions:
  general:
    - "Write clean, readable, and maintainable code"
    - "Use TypeScript for all new files"
    - "Follow existing code patterns and conventions"
    - "Add comprehensive comments for complex logic"
  
  code_style:
    - "Use functional components in React"
    - "Prefer arrow functions"
    - "Use meaningful variable names"
    - "Follow ESLint configuration"
  
  architecture:
    - "Follow the existing folder structure"
    - "Separate concerns into different modules"
    - "Use custom hooks for reusable logic"
    - "Keep components small and focused"

examples:
  react_component: |
    ```typescript
    interface Props {
      title: string;
      onClick: () => void;
    }
    
    export const Button: React.FC<Props> = ({ title, onClick }) => {
      return (
        <button onClick={onClick} className="btn">
          {title}
        </button>
      );
    };
    ```

variables:
  project_name: "${PROJECT_NAME}"
  author_name: "${AUTHOR_NAME}"
  tech_stack: "${TECH_STACK}"

editor_specific:
  copilot:
    additional_instructions:
      - "Focus on code completion and suggestions"
      - "Provide context-aware variable names"
    
  cursor:
    additional_instructions:
      - "Be concise in explanations"
      - "Focus on quick implementations"
    
  continue:
    custom_commands:
      - name: "explain"
        prompt: "Explain this code in detail"
      - name: "optimize"
        prompt: "Suggest optimizations for this code"
```

### 2. CLI Tool (promptrek)

**Purpose**: Command-line interface for generating editor-specific prompts

**Commands**:
```bash
# Initialize a new universal prompt file
promptrek init

# Generate prompts for specific editor
promptrek generate --editor copilot
promptrek generate --editor cursor
promptrek generate --editor continue

# Generate for all configured editors
promptrek generate --all

# List supported editors
promptrek list-editors

# Validate universal prompt file
promptrek validate

# Show generated output without writing files
promptrek preview --editor copilot
```

**Configuration File** (`.promptrek.config.json`):
```json
{
  "default_editors": ["copilot", "cursor"],
  "output_directory": ".ai-prompts",
  "template_directory": "~/.promptrek/templates",
  "variables": {
    "PROJECT_NAME": "My Project",
    "AUTHOR_NAME": "John Doe",
    "TECH_STACK": "React, TypeScript, Node.js"
  }
}
```

### 3. Template Engine

**Purpose**: Convert universal format to editor-specific formats

**Template Structure**:
```
templates/
├── copilot/
│   ├── instructions.md.j2
│   └── config.json.j2
├── cursor/
│   └── cursorrules.j2
├── continue/
│   └── config.json.j2
└── shared/
    ├── common.md.j2
    └── examples.md.j2
```

**Template Example** (`copilot/instructions.md.j2`):
```markdown
# {{ metadata.title }}

{{ context.description }}

## Project Information
- Type: {{ context.project_type }}
- Technologies: {{ context.technologies | join(', ') }}

## General Instructions
{% for instruction in instructions.general %}
- {{ instruction }}
{% endfor %}

## Code Style Guidelines
{% for guideline in instructions.code_style %}
- {{ guideline }}
{% endfor %}

{% if examples %}
## Examples
{% for name, example in examples.items() %}
### {{ name | title }}
{{ example }}
{% endfor %}
{% endif %}

{% if editor_specific.copilot %}
## Copilot-Specific Instructions
{% for instruction in editor_specific.copilot.additional_instructions %}
- {{ instruction }}
{% endfor %}
{% endif %}
```

### 4. Editor Adapters

**Purpose**: Handle editor-specific logic and file generation

**Adapter Interface**:
```python
class EditorAdapter:
    def __init__(self, name: str, templates_path: str):
        self.name = name
        self.templates_path = templates_path
    
    def generate(self, universal_prompt: dict, output_path: str) -> List[str]:
        """Generate editor-specific files"""
        pass
    
    def validate(self, universal_prompt: dict) -> List[str]:
        """Validate prompt for this editor"""
        pass
    
    def get_output_files(self) -> List[str]:
        """Get list of files this adapter generates"""
        pass
```

**Copilot Adapter**:
```python
class CopilotAdapter(EditorAdapter):
    def generate(self, universal_prompt: dict, output_path: str) -> List[str]:
        # Generate .github/copilot-instructions.md
        template = self.load_template('instructions.md.j2')
        content = template.render(universal_prompt)
        
        files = []
        # Write to .github/copilot-instructions.md
        github_path = os.path.join(output_path, '.github', 'copilot-instructions.md')
        self.write_file(github_path, content)
        files.append(github_path)
        
        # Optionally write to .copilot/instructions.md
        copilot_path = os.path.join(output_path, '.copilot', 'instructions.md')
        self.write_file(copilot_path, content)
        files.append(copilot_path)
        
        return files
```

## Data Flow

1. **Input**: User creates universal prompt file (`.promptrek.yaml`)
2. **Processing**: CLI tool reads the file and processes it
3. **Template Resolution**: Template engine selects appropriate templates
4. **Variable Substitution**: Replace variables with actual values
5. **Editor Adaptation**: Apply editor-specific transformations
6. **Output Generation**: Write editor-specific files to appropriate locations

## File Structure

```
project-root/
├── .promptrek.yaml                    # Universal prompt file
├── .promptrek.config.json            # Project configuration
├── .github/
│   └── copilot-instructions.md # Generated Copilot prompts
├── .cursorrules                # Generated Cursor prompts
├── .continue/
│   └── config.json             # Generated Continue prompts
└── .ai-prompts/                # Optional: centralized output directory
    ├── copilot/
    ├── cursor/
    └── continue/
```

## Technology Stack Considerations

### Language Options
1. **Python**: Rich ecosystem, good templating (Jinja2), cross-platform
2. **Node.js**: JavaScript ecosystem, good for web developers
3. **Go**: Fast, single binary, good CLI tools
4. **Rust**: Performance, safety, growing ecosystem

### Recommended: Python
- **Pros**: Rich templating ecosystem, easy to extend, good CLI libraries
- **Cons**: Requires Python runtime
- **Libraries**: Click (CLI), Jinja2 (templating), PyYAML (parsing)

### Alternative: Node.js
- **Pros**: Familiar to web developers, good package ecosystem
- **Cons**: Node.js runtime required
- **Libraries**: Commander.js (CLI), Handlebars (templating), js-yaml (parsing)

## Security Considerations

1. **Template Injection**: Validate template content and user input
2. **File Permissions**: Ensure generated files have appropriate permissions
3. **Path Traversal**: Validate output paths to prevent writing outside project
4. **Variable Injection**: Sanitize variable values in templates

## Extensibility Design

### Adding New Editors
1. Create new adapter class
2. Add templates for the editor
3. Register adapter in the system
4. Update documentation

### Custom Templates
1. User-defined template directories
2. Template inheritance and overrides
3. Plugin system for custom transformations

### Configuration Layers
1. Global configuration (`~/.promptrek/config.json`)
2. Project configuration (`.promptrek.config.json`)
3. Command-line overrides