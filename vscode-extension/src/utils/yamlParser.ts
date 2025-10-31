/**
 * YAML parsing utilities for PrompTrek configuration files
 */

import * as vscode from 'vscode';
import * as yaml from 'js-yaml';
import * as fs from 'fs';
import { PrompTrekConfig } from '../types/promptrek';

export class YamlParser {
  /**
   * Parse a PrompTrek YAML file
   */
  static async parseFile(filePath: string): Promise<PrompTrekConfig | null> {
    try {
      const content = await fs.promises.readFile(filePath, 'utf8');
      return this.parseContent(content);
    } catch (error) {
      console.error(`Error reading file ${filePath}:`, error);
      return null;
    }
  }

  /**
   * Parse PrompTrek YAML content
   */
  static parseContent(content: string): PrompTrekConfig | null {
    try {
      const config = yaml.load(content) as PrompTrekConfig;
      return config;
    } catch (error) {
      console.error('Error parsing YAML:', error);
      return null;
    }
  }

  /**
   * Find PrompTrek configuration files in workspace
   */
  static async findConfigFiles(): Promise<vscode.Uri[]> {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders) {
      return [];
    }

    const files: vscode.Uri[] = [];

    for (const folder of workspaceFolders) {
      const pattern = new vscode.RelativePattern(folder, '**/*.promptrek.yaml');
      const foundFiles = await vscode.workspace.findFiles(pattern);
      files.push(...foundFiles);
    }

    return files;
  }

  /**
   * Get the primary config file (project.promptrek.yaml or first found)
   */
  static async getPrimaryConfigFile(): Promise<vscode.Uri | null> {
    const files = await this.findConfigFiles();

    if (files.length === 0) {
      return null;
    }

    // Look for project.promptrek.yaml first
    const primaryFile = files.find(file =>
      file.fsPath.endsWith('project.promptrek.yaml')
    );

    return primaryFile || files[0];
  }

  /**
   * Validate basic structure of a PrompTrek config
   */
  static validate(config: PrompTrekConfig): string[] {
    const errors: string[] = [];

    if (!config.schema_version) {
      errors.push('Missing schema_version field');
    }

    if (!config.content) {
      errors.push('Missing content field');
    }

    // Schema version validation
    const validVersions = ['1.0.0', '2.0.0', '2.1.0', '3.0.0', '3.1.0'];
    if (config.schema_version && !validVersions.includes(config.schema_version)) {
      errors.push(`Invalid schema_version: ${config.schema_version}`);
    }

    return errors;
  }

  /**
   * Get schema version from config
   */
  static getSchemaVersion(config: PrompTrekConfig): string {
    return config.schema_version || 'unknown';
  }

  /**
   * Check if config has plugins
   */
  static hasPlugins(config: PrompTrekConfig): boolean {
    return !!(
      config.mcp_servers?.length ||
      config.commands?.length ||
      config.agents?.length ||
      config.hooks?.length
    );
  }

  /**
   * Get plugin count
   */
  static getPluginCount(config: PrompTrekConfig): {
    mcpServers: number;
    commands: number;
    agents: number;
    hooks: number;
    total: number;
  } {
    const mcpServers = config.mcp_servers?.length || 0;
    const commands = config.commands?.length || 0;
    const agents = config.agents?.length || 0;
    const hooks = config.hooks?.length || 0;

    return {
      mcpServers,
      commands,
      agents,
      hooks,
      total: mcpServers + commands + agents + hooks
    };
  }
}
