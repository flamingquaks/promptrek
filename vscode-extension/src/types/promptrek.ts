/**
 * TypeScript type definitions for PrompTrek configuration
 */

export interface PrompTrekMetadata {
  title?: string;
  description?: string;
  version?: string;
  author?: string;
  tags?: string[];
}

export interface PrompTrekDocument {
  name: string;
  content: string;
  description?: string;
  file_globs?: string | string[];
  always_apply?: boolean;
}

export interface MCPServer {
  name: string;
  command: string;
  args?: string[];
  env?: Record<string, string>;
  description?: string;
  trust_metadata?: {
    trusted: boolean;
    trust_level: 'full' | 'partial' | 'minimal';
  };
}

export interface CustomCommand {
  name: string;
  description: string;
  prompt: string;
  output_format?: string;
}

export interface Agent {
  name: string;
  description: string;
  prompt?: string; // v3.1 field
  system_prompt?: string; // legacy field
  tools?: string[];
  trust_level?: 'full' | 'partial' | 'minimal';
  requires_approval?: boolean;
}

export interface EventHook {
  event: string;
  command: string;
  description?: string;
}

export interface PrompTrekConfig {
  schema_version: string;
  metadata?: PrompTrekMetadata;
  content: string;
  variables?: Record<string, string>;
  documents?: PrompTrekDocument[];
  mcp_servers?: MCPServer[];
  commands?: CustomCommand[];
  agents?: Agent[];
  hooks?: EventHook[];
  ignore_editor_files?: boolean;
}

export interface EditorInfo {
  name: string;
  displayName: string;
  description: string;
  filePatterns: string[];
  supported: boolean;
  hasProjectConfig: boolean;
}

export const SUPPORTED_EDITORS: EditorInfo[] = [
  {
    name: 'copilot',
    displayName: 'GitHub Copilot',
    description: 'GitHub Copilot Instructions',
    filePatterns: ['.github/copilot-instructions.md'],
    supported: true,
    hasProjectConfig: true
  },
  {
    name: 'cursor',
    displayName: 'Cursor',
    description: 'Cursor Rules',
    filePatterns: ['.cursor/rules/index.mdc'],
    supported: true,
    hasProjectConfig: true
  },
  {
    name: 'continue',
    displayName: 'Continue',
    description: 'Continue Rules',
    filePatterns: ['.continue/rules/*.md'],
    supported: true,
    hasProjectConfig: true
  },
  {
    name: 'claude',
    displayName: 'Claude Code',
    description: 'Claude Code Configuration',
    filePatterns: ['.claude/CLAUDE.md', '.mcp.json'],
    supported: true,
    hasProjectConfig: true
  },
  {
    name: 'windsurf',
    displayName: 'Windsurf',
    description: 'Windsurf Rules',
    filePatterns: ['.windsurf/rules/*.md'],
    supported: true,
    hasProjectConfig: true
  },
  {
    name: 'cline',
    displayName: 'Cline',
    description: 'Cline Rules',
    filePatterns: ['.clinerules/*.md'],
    supported: true,
    hasProjectConfig: true
  },
  {
    name: 'kiro',
    displayName: 'Kiro',
    description: 'Kiro Steering',
    filePatterns: ['.kiro/steering/*.md'],
    supported: true,
    hasProjectConfig: true
  },
  {
    name: 'amazon-q',
    displayName: 'Amazon Q',
    description: 'Amazon Q Rules',
    filePatterns: ['.amazonq/rules/*.md'],
    supported: true,
    hasProjectConfig: true
  },
  {
    name: 'jetbrains',
    displayName: 'JetBrains AI',
    description: 'JetBrains AI Assistant',
    filePatterns: ['.assistant/rules/*.md'],
    supported: true,
    hasProjectConfig: true
  }
];
