---
layout: default
title: Home
---

# PrompTrek

*Taking your coding prompts on a journey to every AI editor!*

A universal AI Editor prompt storage solution that dynamically maps prompt data to a wide-range of agentic/AI editors and tools. This tool allows you to create generic prompts and workflows in a standardized format, then generate editor-specific prompts for your preferred AI coding assistant.

## 🎯 The Problem

AI coding assistants like GitHub Copilot, Cursor, Continue, and others all use different prompt formats and configuration methods. When working across teams or switching between editors, you have to:

- **Maintain separate configurations** for each AI editor
- **Recreate prompts** when switching tools
- **Struggle with team consistency** when members use different editors
- **Face migration headaches** when adopting new AI tools

## 🚀 The Solution

PrompTrek solves these challenges by providing:

- **Universal Format**: Create prompts once in a standardized format
- **Multi-Editor Support**: Generate prompts for any supported AI editor
- **Team Consistency**: Share prompt configurations across team members regardless of their editor choice
- **Easy Migration**: Switch between AI editors without losing your prompt configurations

## 🎨 Supported Editors

### ✅ Fully Supported
- **GitHub Copilot** - Repository-wide and path-specific instructions
- **Cursor** - Modern rules with YAML frontmatter and glob patterns
- **Continue** - Complete YAML configuration system
- **Amazon Q** - Comment-based assistance templates
- **JetBrains AI** - IDE-integrated prompts
- **Kiro** - Comprehensive steering and specification files
- **Cline** - Markdown-based rules

## 🚀 Quick Start

### 1. Installation

```bash
pip install promptrek
```

### 2. Create Your First Universal Prompt

```bash
# Initialize a new prompt file
promptrek init --output my-project.promptrek.yaml
```

### 3. Generate Editor-Specific Prompts

```bash
# Generate for specific editor
promptrek generate --editor copilot

# Generate for all configured editors
promptrek generate --all
```

## 📋 Quick Example

Create a universal prompt file (`.promptrek.yaml`):

```yaml
schema_version: "1.0.0"
metadata:
  title: "My Project Assistant"
  description: "AI assistant for React TypeScript project"
targets: [copilot, cursor, continue]
instructions:
  general:
    - "Use TypeScript for all new files"
    - "Follow React functional component patterns"
    - "Write comprehensive tests"
```

Then generate editor-specific prompts:

```bash
promptrek generate --all
```

PrompTrek will create the appropriate configuration files for each editor!

## 🎯 Key Features

### 🔄 Variable Substitution
Use dynamic variables in your prompts that get substituted during generation.

### 🎯 Conditional Instructions
Apply different instructions based on project context or target editor.

### 📦 Import System
Organize and reuse prompt components across multiple configurations.

### 🎨 Multiple Editor Support
Generate prompts for all major AI coding assistants from a single source.

## 🔗 Quick Links

- [**Quick Start Guide**](quick-start.html) - Get up and running in minutes
- [**User Guide**](user-guide.html) - Comprehensive documentation
- [**Contributing**](contributing.html) - Help improve PrompTrek
- [**Report Issues**]({{ site.issues_url }}) - Found a bug or have a feature request?

---

## 🏆 Why PrompTrek?

**For Individual Developers:**
- Work seamlessly across different AI editors
- Maintain consistent coding standards
- Easy experimentation with new AI tools

**For Teams:**
- Standardized AI assistance across all team members
- Easy onboarding regardless of editor preference  
- Consistent code quality and patterns

**For Organizations:**
- Reduce tool lock-in and migration costs
- Standardize AI-assisted development practices
- Scale AI adoption across diverse teams

Ready to get started? Check out our [Quick Start Guide](quick-start.html)!