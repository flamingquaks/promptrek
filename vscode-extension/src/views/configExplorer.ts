/**
 * PrompTrek Configuration Explorer Tree View
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { YamlParser } from '../utils/yamlParser';
import { PrompTrekConfig } from '../types/promptrek';

export class ConfigExplorerProvider implements vscode.TreeDataProvider<ConfigItem> {
  private _onDidChangeTreeData: vscode.EventEmitter<ConfigItem | undefined | null | void> =
    new vscode.EventEmitter<ConfigItem | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<ConfigItem | undefined | null | void> =
    this._onDidChangeTreeData.event;

  private currentConfig: PrompTrekConfig | null = null;
  private currentConfigFile: vscode.Uri | null = null;

  constructor() {
    this.loadConfig();
  }

  refresh(): void {
    this.loadConfig();
    this._onDidChangeTreeData.fire();
  }

  private async loadConfig(): Promise<void> {
    const configFile = await YamlParser.getPrimaryConfigFile();
    if (configFile) {
      this.currentConfigFile = configFile;
      this.currentConfig = await YamlParser.parseFile(configFile.fsPath);
    } else {
      this.currentConfigFile = null;
      this.currentConfig = null;
    }
  }

  getTreeItem(element: ConfigItem): vscode.TreeItem {
    return element;
  }

  async getChildren(element?: ConfigItem): Promise<ConfigItem[]> {
    if (!this.currentConfig || !this.currentConfigFile) {
      return [
        new ConfigItem(
          'No Configuration Found',
          '',
          vscode.TreeItemCollapsibleState.None,
          'info',
          'info'
        )
      ];
    }

    if (!element) {
      // Root level
      return [
        new ConfigItem(
          path.basename(this.currentConfigFile.fsPath),
          this.currentConfigFile.fsPath,
          vscode.TreeItemCollapsibleState.Expanded,
          'configFile',
          'file'
        ),
        new ConfigItem(
          'Metadata',
          '',
          vscode.TreeItemCollapsibleState.Collapsed,
          'metadata',
          'tag'
        ),
        new ConfigItem(
          'Variables',
          `${Object.keys(this.currentConfig.variables || {}).length} defined`,
          vscode.TreeItemCollapsibleState.Collapsed,
          'variables',
          'symbol-variable'
        ),
        new ConfigItem(
          'Content',
          `${this.currentConfig.content.split('\n').length} lines`,
          vscode.TreeItemCollapsibleState.None,
          'content',
          'note'
        ),
        new ConfigItem(
          'Plugins',
          this.getPluginsSummary(),
          vscode.TreeItemCollapsibleState.Collapsed,
          'plugins',
          'extensions'
        ),
        new ConfigItem(
          'Documents',
          `${this.currentConfig.documents?.length || 0} defined`,
          vscode.TreeItemCollapsibleState.Collapsed,
          'documents',
          'files'
        )
      ];
    }

    // Child items based on parent type
    switch (element.contextValue) {
      case 'configFile':
        return [
          new ConfigItem(
            `Schema: ${this.currentConfig.schema_version}`,
            '',
            vscode.TreeItemCollapsibleState.None,
            'schema',
            'symbol-numeric'
          )
        ];

      case 'metadata':
        return this.getMetadataItems();

      case 'variables':
        return this.getVariableItems();

      case 'plugins':
        return this.getPluginItems();

      case 'documents':
        return this.getDocumentItems();

      case 'mcpServers':
        return this.getMcpServerItems();

      case 'commands':
        return this.getCommandItems();

      case 'agents':
        return this.getAgentItems();

      case 'hooks':
        return this.getHookItems();

      default:
        return [];
    }
  }

  private getPluginsSummary(): string {
    if (!this.currentConfig) return '0 total';
    const counts = YamlParser.getPluginCount(this.currentConfig);
    return `${counts.total} total`;
  }

  private getMetadataItems(): ConfigItem[] {
    const metadata = this.currentConfig?.metadata;
    if (!metadata) {
      return [
        new ConfigItem(
          'No metadata defined',
          '',
          vscode.TreeItemCollapsibleState.None,
          'empty',
          'info'
        )
      ];
    }

    const items: ConfigItem[] = [];
    if (metadata.title) {
      items.push(
        new ConfigItem(
          `Title: ${metadata.title}`,
          '',
          vscode.TreeItemCollapsibleState.None,
          'metadataItem',
          'symbol-string'
        )
      );
    }
    if (metadata.description) {
      items.push(
        new ConfigItem(
          `Description: ${metadata.description}`,
          '',
          vscode.TreeItemCollapsibleState.None,
          'metadataItem',
          'symbol-string'
        )
      );
    }
    if (metadata.version) {
      items.push(
        new ConfigItem(
          `Version: ${metadata.version}`,
          '',
          vscode.TreeItemCollapsibleState.None,
          'metadataItem',
          'symbol-string'
        )
      );
    }
    if (metadata.author) {
      items.push(
        new ConfigItem(
          `Author: ${metadata.author}`,
          '',
          vscode.TreeItemCollapsibleState.None,
          'metadataItem',
          'account'
        )
      );
    }
    if (metadata.tags) {
      items.push(
        new ConfigItem(
          `Tags: ${metadata.tags.join(', ')}`,
          '',
          vscode.TreeItemCollapsibleState.None,
          'metadataItem',
          'tag'
        )
      );
    }

    return items;
  }

  private getVariableItems(): ConfigItem[] {
    const variables = this.currentConfig?.variables;
    if (!variables || Object.keys(variables).length === 0) {
      return [
        new ConfigItem(
          'No variables defined',
          '',
          vscode.TreeItemCollapsibleState.None,
          'empty',
          'info'
        )
      ];
    }

    return Object.entries(variables).map(
      ([key, value]) =>
        new ConfigItem(
          `${key}`,
          `${value}`,
          vscode.TreeItemCollapsibleState.None,
          'variable',
          'symbol-variable'
        )
    );
  }

  private getPluginItems(): ConfigItem[] {
    if (!this.currentConfig) return [];

    const counts = YamlParser.getPluginCount(this.currentConfig);
    const items: ConfigItem[] = [];

    if (counts.mcpServers > 0) {
      items.push(
        new ConfigItem(
          'MCP Servers',
          `${counts.mcpServers} configured`,
          vscode.TreeItemCollapsibleState.Collapsed,
          'mcpServers',
          'server'
        )
      );
    }

    if (counts.commands > 0) {
      items.push(
        new ConfigItem(
          'Custom Commands',
          `${counts.commands} defined`,
          vscode.TreeItemCollapsibleState.Collapsed,
          'commands',
          'symbol-method'
        )
      );
    }

    if (counts.agents > 0) {
      items.push(
        new ConfigItem(
          'Agents',
          `${counts.agents} defined`,
          vscode.TreeItemCollapsibleState.Collapsed,
          'agents',
          'robot'
        )
      );
    }

    if (counts.hooks > 0) {
      items.push(
        new ConfigItem(
          'Event Hooks',
          `${counts.hooks} defined`,
          vscode.TreeItemCollapsibleState.Collapsed,
          'hooks',
          'symbol-event'
        )
      );
    }

    if (items.length === 0) {
      items.push(
        new ConfigItem(
          'No plugins configured',
          '',
          vscode.TreeItemCollapsibleState.None,
          'empty',
          'info'
        )
      );
    }

    return items;
  }

  private getDocumentItems(): ConfigItem[] {
    const documents = this.currentConfig?.documents;
    if (!documents || documents.length === 0) {
      return [
        new ConfigItem(
          'No documents defined',
          '',
          vscode.TreeItemCollapsibleState.None,
          'empty',
          'info'
        )
      ];
    }

    return documents.map(
      doc =>
        new ConfigItem(
          doc.name,
          doc.description || '',
          vscode.TreeItemCollapsibleState.None,
          'document',
          'file-text'
        )
    );
  }

  private getMcpServerItems(): ConfigItem[] {
    const servers = this.currentConfig?.mcp_servers || [];
    return servers.map(
      server =>
        new ConfigItem(
          server.name,
          server.description || `${server.command} ${server.args?.join(' ') || ''}`,
          vscode.TreeItemCollapsibleState.None,
          'mcpServer',
          'server-process'
        )
    );
  }

  private getCommandItems(): ConfigItem[] {
    const commands = this.currentConfig?.commands || [];
    return commands.map(
      cmd =>
        new ConfigItem(
          cmd.name,
          cmd.description,
          vscode.TreeItemCollapsibleState.None,
          'command',
          'terminal'
        )
    );
  }

  private getAgentItems(): ConfigItem[] {
    const agents = this.currentConfig?.agents || [];
    return agents.map(
      agent =>
        new ConfigItem(
          agent.name,
          agent.description,
          vscode.TreeItemCollapsibleState.None,
          'agent',
          'hubot'
        )
    );
  }

  private getHookItems(): ConfigItem[] {
    const hooks = this.currentConfig?.hooks || [];
    return hooks.map(
      hook =>
        new ConfigItem(
          hook.event,
          hook.description || hook.command,
          vscode.TreeItemCollapsibleState.None,
          'hook',
          'debug-breakpoint'
        )
    );
  }
}

class ConfigItem extends vscode.TreeItem {
  constructor(
    public readonly label: string,
    public readonly description: string,
    public readonly collapsibleState: vscode.TreeItemCollapsibleState,
    public readonly contextValue: string,
    public readonly iconName: string
  ) {
    super(label, collapsibleState);
    this.description = description;
    this.contextValue = contextValue;
    this.iconId = new vscode.ThemeIcon(iconName);

    // Make config file clickable
    if (contextValue === 'configFile') {
      this.command = {
        command: 'promptrek.openConfig',
        title: 'Open Configuration',
        arguments: []
      };
    }
  }
}
