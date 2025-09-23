# AI Editors Research

## Overview

This document contains research on various AI editors and their prompt formats, configuration methods, and integration approaches.

## AI Editors and Tools

### 1. GitHub Copilot

**Description**: AI pair programmer integrated with various IDEs
**Prompt Format**: 
- `.github/copilot-instructions.md` (global)
- `.copilot/instructions.md` (repository level)
- Inline comments for context

**Features**:
- Supports markdown instructions
- Context-aware suggestions
- Works with multiple IDEs (VS Code, JetBrains, Vim, etc.)
- Custom instructions for repositories

**File Locations**:
```
.github/copilot-instructions.md
.copilot/instructions.md
```

**Example Format**:
```markdown
# Project Instructions

## Context
This is a React application...

## Coding Standards
- Use TypeScript
- Prefer functional components
- Use ESLint rules
```

### 2. Cursor

**Description**: AI-first code editor
**Prompt Format**:
- `.cursorrules` file in project root
- Inline prompts within code
- Chat-based interactions

**Features**:
- Custom rules files
- Context-aware AI assistance
- Built-in AI chat
- File-level and project-level instructions

**File Locations**:
```
.cursorrules
```

**Example Format**:
```
# Cursor Rules

## General Guidelines
- Write clean, readable code
- Use TypeScript for all new files
- Follow existing patterns

## Specific Instructions
- For React components, use functional components
- For API calls, use the existing fetch wrapper
```

### 3. Continue

**Description**: Open-source Copilot alternative
**Prompt Format**:
- `continue/config.json` configuration
- Custom prompts in JSON format
- System messages and user instructions

**Features**:
- Highly customizable
- Multiple AI model support
- Custom prompt templates
- Context providers

**File Locations**:
```
.continue/config.json
```

**Example Format**:
```json
{
  "models": [...],
  "customCommands": [
    {
      "name": "explain",
      "prompt": "Please explain this code: {{{ input }}}"
    }
  ],
  "systemMessage": "You are a helpful coding assistant..."
}
```

### 4. Codeium

**Description**: Free AI code completion and chat
**Prompt Format**:
- Context-based suggestions
- Chat interface
- Custom instructions through comments

**Features**:
- Multi-language support
- IDE integrations
- Context-aware suggestions
- Chat-based assistance

### 5. Tabnine

**Description**: AI code completion tool
**Prompt Format**:
- Team-specific models
- Custom training on codebases
- Configuration through IDE settings

**Features**:
- Team collaboration
- Custom model training
- Privacy-focused options
- Enterprise features

### 6. Amazon CodeWhisperer (now Amazon Q)

**Description**: AI coding companion
**Prompt Format**:
- Comment-based prompts
- Natural language to code
- IDE-specific configurations

**Features**:
- AWS integration
- Security scanning
- Multi-language support
- Reference tracking

### 7. JetBrains AI Assistant

**Description**: Built-in AI for JetBrains IDEs
**Prompt Format**:
- Chat interface
- Context-aware suggestions
- IDE-integrated prompts

**Features**:
- Deep IDE integration
- Language-specific assistance
- Code generation and explanation
- Refactoring suggestions

### 8. Claude Code

**Description**: AI coding assistant powered by Anthropic's Claude
**Prompt Format**:
- Context-based prompts
- Natural language instructions
- Project-specific configurations

**Features**:
- Advanced reasoning capabilities
- Code understanding and explanation
- Multi-language support
- Safety-focused AI assistance

### 9. Kiro

**Description**: AI-powered code assistance and automation
**Prompt Format**:
- Configuration-based prompts
- Workflow automation rules
- Context-aware suggestions

**Features**:
- Intelligent code suggestions
- Automated code reviews
- Development workflow integration
- Team collaboration features

### 10. Cline

**Description**: Terminal-based AI coding assistant
**Prompt Format**:
- Command-line prompts
- Terminal integration
- Script-based configurations

**Features**:
- CLI-native interface
- Terminal workflow integration
- Script automation
- Command-line productivity tools
- IDE-integrated prompts

**Features**:
- Deep IDE integration
- Language-specific assistance
- Code generation and explanation
- Refactoring suggestions

## Common Patterns

### File-Based Configuration
Most editors support file-based configuration:
- **Copilot**: `.github/copilot-instructions.md`, `.copilot/instructions.md`
- **Cursor**: `.cursorrules`
- **Continue**: `.continue/config.json`

### Prompt Structure Elements
Common elements across different editors:
1. **Context/Background**: Project description and purpose
2. **Coding Standards**: Style guides and conventions
3. **Architecture Guidelines**: Patterns and best practices
4. **Specific Instructions**: Tool-specific guidance
5. **Examples**: Code samples and templates

### Integration Methods
1. **File-based**: Configuration files in project root
2. **Comment-based**: Inline comments for context
3. **Chat-based**: Interactive prompt interfaces
4. **JSON/YAML**: Structured configuration formats

## Key Insights for Universal Format

### Universal Elements Needed
1. **Metadata**: Title, description, version, target editors
2. **Context**: Project background and purpose
3. **Instructions**: General and editor-specific guidance
4. **Examples**: Code samples and templates
5. **Variables**: Placeholder values for customization
6. **Conditions**: Editor-specific or conditional instructions

### Mapping Strategy
1. **Direct Mapping**: Simple text-to-text conversion
2. **Template Processing**: Variable substitution and formatting
3. **Conditional Logic**: Include/exclude based on target editor
4. **Format Transformation**: Convert between markdown, JSON, plain text
5. **File Organization**: Generate appropriate file structures

### Extensibility Considerations
1. **Plugin Architecture**: Easy to add new editor support
2. **Template System**: Customizable output formats
3. **Configuration Overrides**: Project and user-level customizations
4. **Validation**: Ensure generated prompts meet editor requirements