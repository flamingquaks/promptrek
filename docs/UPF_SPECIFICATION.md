# Universal Prompt Format (UPF) Specification

## Overview

The Universal Prompt Format (UPF) is a standardized YAML-based format for defining AI assistant prompts that can be converted to various editor-specific formats.

## File Extension

`.promptrek.yaml`

## Schema Version

Current version: `1.0.0`

## Complete Schema

```yaml
# Schema version (required)
schema_version: "1.0.0"

# Metadata about the prompt file (required)
metadata:
  title: string                    # Human-readable title (required)
  description: string              # Brief description of purpose (required)
  version: string                  # Semantic version of this prompt (optional)
  author: string                   # Author name or email (optional)
  created: string                  # ISO 8601 date (YYYY-MM-DD) (optional)
  updated: string                  # ISO 8601 date (YYYY-MM-DD) (optional)
  tags: [string]                   # Tags for categorization (optional)

# Target editors this prompt supports (optional)
targets:
  - string                         # List of supported editor names (optional)

# Project context information (optional)
context:
  project_type: string             # e.g., "web_application", "api", "library"
  technologies: [string]           # List of technologies used
  description: string              # Detailed project description
  repository_url: string           # Optional repository URL
  documentation_url: string        # Optional documentation URL

# Main instructions (required)
instructions:
  general: [string]                # General coding guidelines
  code_style: [string]             # Code style and formatting rules
  architecture: [string]           # Architectural patterns and principles
  testing: [string]                # Testing guidelines
  documentation: [string]          # Documentation requirements
  security: [string]               # Security considerations
  performance: [string]            # Performance guidelines

# Workflows and automation (optional)
workflows:
  development: [string]            # Development workflow steps
  review: [string]                 # Code review workflow
  testing: [string]               # Testing workflow steps
  deployment: [string]             # Deployment workflow
  collaboration: [string]          # Team collaboration workflows

# Code examples and templates (optional)
examples:
  example_name: string             # Code example in markdown format
  # ... more examples

# Template variables (optional)
variables:
  variable_name: string            # Default value or placeholder
  # ... more variables

# Editor-specific configurations (optional)
editor_specific:
  editor_name:
    additional_instructions: [string]
    custom_commands: 
      - name: string
        prompt: string
        description: string
    templates:
      template_name: string
    # ... editor-specific fields

# Conditional instructions (optional)
conditions:
  - if: string                     # Condition expression
    then:
      instructions: [string]
      examples: {}
    else:                          # Optional
      instructions: [string]
      examples: {}

# Import other prompt files (optional)
imports:
  - path: string                   # Relative path to another .promptrek.yaml file
    prefix: string                 # Optional namespace prefix
```

## Detailed Field Descriptions

### metadata (required)

Contains information about the prompt file itself.

**Fields**:
- `title`: Human-readable title for the prompt set
- `description`: Brief description of what this prompt configuration is for
- `version`: Semantic version of this prompt file (for tracking changes)
- `author`: Author name or email address
- `created`: Creation date in ISO 8601 format (YYYY-MM-DD)
- `updated`: Last update date in ISO 8601 format (YYYY-MM-DD)
- `tags`: Array of tags for categorization and filtering

**Example**:
```yaml
metadata:
  title: "React TypeScript Project Assistant"
  description: "AI assistant configuration for React projects with TypeScript"
  version: "1.2.0"
  author: "john.doe@example.com"
  created: "2024-01-01"
  updated: "2024-01-15"
  tags: ["react", "typescript", "frontend"]
```

### targets (required)

List of AI editors/tools that this prompt configuration supports.

**Supported Values**:
- `copilot`: GitHub Copilot
- `cursor`: Cursor editor
- `continue`: Continue extension
- `claude_code`: Claude Code
- `kiro`: Kiro AI assistant
- `cline`: Cline terminal assistant
- `codeium`: Codeium
- `tabnine`: Tabnine
- `amazon_q`: Amazon Q (formerly CodeWhisperer)
- `jetbrains_ai`: JetBrains AI Assistant

**Example**:
```yaml
targets:
  - copilot
  - cursor
  - continue
```

### context (optional)

Provides context about the project to help AI assistants understand the codebase.

**Fields**:
- `project_type`: Type of project (web_application, api, library, mobile_app, etc.)
- `technologies`: Array of technologies, frameworks, and languages used
- `description`: Detailed description of the project's purpose and architecture
- `repository_url`: URL to the project repository
- `documentation_url`: URL to project documentation

**Example**:
```yaml
context:
  project_type: "web_application"
  technologies:
    - "typescript"
    - "react"
    - "node.js"
    - "express"
    - "postgresql"
  description: |
    A modern e-commerce web application built with React and TypeScript.
    Uses a microservices architecture with Node.js backends and PostgreSQL databases.
  repository_url: "https://github.com/company/ecommerce-app"
  documentation_url: "https://docs.company.com/ecommerce-app"
```

### instructions (required)

The main set of instructions for AI assistants. At least one instruction category must be present.

**Categories**:
- `general`: General coding guidelines and principles
- `code_style`: Code style, formatting, and naming conventions
- `architecture`: Architectural patterns and design principles
- `testing`: Testing strategies and requirements
- `documentation`: Documentation standards and requirements
- `security`: Security considerations and best practices
- `performance`: Performance optimization guidelines

**Example**:
```yaml
instructions:
  general:
    - "Write clean, readable, and maintainable code"
    - "Use TypeScript for all new files"
    - "Follow existing code patterns and conventions"
    - "Add comprehensive comments for complex logic"
  
  code_style:
    - "Use functional components in React"
    - "Prefer arrow functions over function declarations"
    - "Use meaningful and descriptive variable names"
    - "Follow the existing ESLint configuration"
  
  architecture:
    - "Follow the existing folder structure"
    - "Separate concerns into different modules"
    - "Use custom hooks for reusable React logic"
    - "Keep components small and focused on a single responsibility"
  
  testing:
    - "Write unit tests for all new functions and components"
    - "Use React Testing Library for component tests"
    - "Aim for at least 80% code coverage"
  
  security:
    - "Sanitize all user inputs"
    - "Use parameterized queries for database operations"
    - "Implement proper authentication and authorization"
```

### workflows (optional)

Defines development workflows and automation guidelines that AI assistants should understand and support.

**Categories**:
- `development`: Development workflow steps and practices
- `review`: Code review workflow and standards
- `testing`: Testing workflow and automation
- `deployment`: Deployment workflow and procedures
- `collaboration`: Team collaboration workflows

**Example**:
```yaml
workflows:
  development:
    - "Start by creating a feature branch from main"
    - "Write tests before implementing functionality (TDD)"
    - "Make small, focused commits with descriptive messages"
    - "Run linting and tests before pushing changes"
  
  review:
    - "Create pull requests with clear descriptions and context"
    - "Request reviews from at least two team members"
    - "Address all review comments before merging"
    - "Ensure CI/CD checks pass before merging"
  
  testing:
    - "Run unit tests locally before committing"
    - "Ensure integration tests pass in CI environment"
    - "Perform manual testing for UI changes"
    - "Update test documentation when adding new test scenarios"
  
  deployment:
    - "Deploy to staging environment first"
    - "Run smoke tests after deployment"
    - "Monitor application logs and metrics"
    - "Have rollback plan ready for production deployments"
  
  collaboration:
    - "Use standardized commit message format"
    - "Update team on progress during daily standups"
    - "Document architectural decisions in ADRs"
    - "Share knowledge through code comments and documentation"
```

### examples (optional)

Code examples and templates that demonstrate best practices.

**Format**: Key-value pairs where the key is a descriptive name and the value is a markdown-formatted code example.

**Example**:
```yaml
examples:
  react_component: |
    ```typescript
    interface ButtonProps {
      title: string;
      onClick: () => void;
      variant?: 'primary' | 'secondary';
    }
    
    export const Button: React.FC<ButtonProps> = ({ 
      title, 
      onClick, 
      variant = 'primary' 
    }) => {
      return (
        <button 
          onClick={onClick} 
          className={`btn btn--${variant}`}
        >
          {title}
        </button>
      );
    };
    ```
  
  api_endpoint: |
    ```typescript
    export const getUserById = async (id: string): Promise<User> => {
      const response = await fetch(`/api/users/${id}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch user: ${response.statusText}`);
      }
      return response.json();
    };
    ```
```

### variables (optional)

Template variables that can be substituted in generated prompts.

**Usage**: Variables are referenced in instructions and examples using `${VARIABLE_NAME}` syntax.

**Example**:
```yaml
variables:
  PROJECT_NAME: "My Awesome Project"
  AUTHOR_NAME: "John Doe"
  TECH_STACK: "React, TypeScript, Node.js"
  API_BASE_URL: "https://api.example.com"

instructions:
  general:
    - "This is the ${PROJECT_NAME} codebase"
    - "Contact ${AUTHOR_NAME} for questions about architecture"
```

### editor_specific (optional)

Editor-specific configurations and additional instructions.

**Structure**: Each editor can have its own section with custom fields.

**Common Fields**:
- `additional_instructions`: Extra instructions specific to this editor
- `custom_commands`: Custom commands or shortcuts (for editors that support them)
- `templates`: Editor-specific templates
- `settings`: Editor-specific settings

**Example**:
```yaml
editor_specific:
  copilot:
    additional_instructions:
      - "Focus on code completion and suggestions"
      - "Provide context-aware variable names"
      - "Generate comprehensive docstrings"
  
  cursor:
    additional_instructions:
      - "Be concise in explanations"
      - "Focus on quick implementations"
    custom_commands:
      - name: "refactor"
        prompt: "Refactor this code to improve readability"
        description: "Improves code structure and readability"
  
  continue:
    custom_commands:
      - name: "explain"
        prompt: "Explain this code in detail: {{{ input }}}"
        description: "Provides detailed code explanation"
      - name: "optimize"
        prompt: "Suggest optimizations for this code: {{{ input }}}"
        description: "Suggests performance improvements"
    settings:
      temperature: 0.7
      max_tokens: 1000
```

### conditions (optional)

Conditional instructions that are applied based on certain criteria.

**Use Cases**:
- Different instructions for different file types
- Environment-specific guidelines (development vs production)
- Technology-specific rules

**Example**:
```yaml
conditions:
  - if: "file_extension == '.test.ts'"
    then:
      instructions:
        - "Focus on comprehensive test coverage"
        - "Use descriptive test names"
        - "Mock external dependencies"
  
  - if: "editor == 'cursor'"
    then:
      instructions:
        - "Provide quick, actionable suggestions"
    else:
      instructions:
        - "Provide detailed explanations"
```

### imports (optional)

Import configurations from other UPF files for modularity and reusability.

**Use Cases**:
- Shared team standards
- Technology-specific configurations
- Organization-wide guidelines

**Example**:
```yaml
imports:
  - path: "../shared/typescript-standards.promptrek.yaml"
    prefix: "ts"
  - path: "./team-conventions.promptrek.yaml"
```

## Validation Rules

1. **Required Fields**: `schema_version`, `metadata`, `targets`, `instructions`
2. **Schema Version**: Must be a valid semantic version string
3. **Targets**: Must contain at least one supported editor name
4. **Instructions**: Must contain at least one instruction category with at least one instruction
5. **Workflows**: All workflow categories are optional, but if present, must contain at least one workflow step
6. **Variables**: Variable names must be valid identifiers (alphanumeric + underscore)
7. **Imports**: Imported files must exist and be valid UPF files

## Example Complete File

```yaml
schema_version: "1.0.0"

metadata:
  title: "React TypeScript E-commerce Project"
  description: "AI assistant configuration for our e-commerce platform"
  version: "2.1.0"
  author: "development-team@company.com"
  created: "2024-01-01"
  updated: "2024-01-15"
  tags: ["react", "typescript", "ecommerce", "frontend"]

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
    - "express"
    - "postgresql"
    - "redis"
  description: |
    A modern e-commerce platform built with React and TypeScript.
    Features include user authentication, product catalog, shopping cart,
    and payment processing. Uses microservices architecture.

instructions:
  general:
    - "Write clean, readable, and maintainable code"
    - "Use TypeScript for all new files"
    - "Follow existing code patterns and conventions"
    - "Add comprehensive comments for complex business logic"
  
  code_style:
    - "Use functional components in React"
    - "Prefer arrow functions over function declarations"
    - "Use meaningful and descriptive variable names"
    - "Follow the existing ESLint and Prettier configuration"
  
  architecture:
    - "Follow the existing folder structure: features/components/hooks/utils"
    - "Separate concerns into different modules"
    - "Use custom hooks for reusable React logic"
    - "Keep components small and focused on a single responsibility"

workflows:
  development:
    - "Create feature branches from main for new features"
    - "Write component tests before implementing React components"
    - "Use Storybook for component documentation and testing"
    - "Run npm run lint and npm run test before committing"
  
  review:
    - "Create detailed PR descriptions with screenshots for UI changes"
    - "Ensure all TypeScript types are properly defined"
    - "Check that new components are properly exported and documented"
    - "Verify accessibility compliance for new UI components"
  
  testing:
    - "Write unit tests for all business logic functions"
    - "Create integration tests for user workflows"
    - "Test components in isolation using React Testing Library"
    - "Ensure e2e tests cover critical user paths"

examples:
  react_component: |
    ```typescript
    interface ProductCardProps {
      product: Product;
      onAddToCart: (product: Product) => void;
    }
    
    export const ProductCard: React.FC<ProductCardProps> = ({ 
      product, 
      onAddToCart 
    }) => {
      return (
        <div className="product-card">
          <img src={product.imageUrl} alt={product.name} />
          <h3>{product.name}</h3>
          <p className="price">${product.price}</p>
          <button onClick={() => onAddToCart(product)}>
            Add to Cart
          </button>
        </div>
      );
    };
    ```

variables:
  PROJECT_NAME: "E-commerce Platform"
  TEAM_EMAIL: "development-team@company.com"

editor_specific:
  copilot:
    additional_instructions:
      - "Generate comprehensive JSDoc comments for public APIs"
      - "Suggest appropriate React hooks for state management"
  
  cursor:
    additional_instructions:
      - "Focus on quick implementations and fixes"
      - "Prioritize performance optimizations"
```