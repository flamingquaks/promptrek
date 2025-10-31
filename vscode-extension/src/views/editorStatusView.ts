/**
 * Editor Status Tree View
 */

import * as vscode from 'vscode';
import { SUPPORTED_EDITORS, EditorInfo } from '../types/promptrek';
import * as fs from 'fs';
import * as path from 'path';

export class EditorStatusProvider implements vscode.TreeDataProvider<EditorItem> {
  private _onDidChangeTreeData: vscode.EventEmitter<EditorItem | undefined | null | void> =
    new vscode.EventEmitter<EditorItem | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<EditorItem | undefined | null | void> =
    this._onDidChangeTreeData.event;

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element: EditorItem): vscode.TreeItem {
    return element;
  }

  async getChildren(element?: EditorItem): Promise<EditorItem[]> {
    if (element) {
      return [];
    }

    // Check which editors have generated files
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceRoot) {
      return [];
    }

    const items: EditorItem[] = [];

    for (const editor of SUPPORTED_EDITORS) {
      const hasFiles = await this.checkEditorFiles(workspaceRoot, editor);
      items.push(new EditorItem(editor, hasFiles));
    }

    return items;
  }

  private async checkEditorFiles(workspaceRoot: string, editor: EditorInfo): Promise<boolean> {
    for (const pattern of editor.filePatterns) {
      // Remove glob patterns for simple check
      const filePath = pattern.replace('*.md', '').replace('*', '');
      const fullPath = path.join(workspaceRoot, filePath);

      try {
        const stats = await fs.promises.stat(fullPath);
        if (stats.isDirectory()) {
          const files = await fs.promises.readdir(fullPath);
          if (files.length > 0) {
            return true;
          }
        } else if (stats.isFile()) {
          return true;
        }
      } catch {
        // File/directory doesn't exist
        continue;
      }
    }

    return false;
  }
}

class EditorItem extends vscode.TreeItem {
  constructor(
    public readonly editorInfo: EditorInfo,
    public readonly hasGeneratedFiles: boolean
  ) {
    super(editorInfo.displayName, vscode.TreeItemCollapsibleState.None);

    this.description = this.hasGeneratedFiles ? '✓ Generated' : 'Not generated';
    this.contextValue = 'editor';

    // Set icon based on status
    if (this.hasGeneratedFiles) {
      this.iconPath = new vscode.ThemeIcon('check', new vscode.ThemeColor('testing.iconPassed'));
    } else {
      this.iconPath = new vscode.ThemeIcon('circle-outline', new vscode.ThemeColor('testing.iconQueued'));
    }

    // Add tooltip with more info
    this.tooltip = new vscode.MarkdownString();
    this.tooltip.appendMarkdown(`**${editorInfo.displayName}**\n\n`);
    this.tooltip.appendMarkdown(`${editorInfo.description}\n\n`);
    this.tooltip.appendMarkdown(`**Files:** ${editorInfo.filePatterns.join(', ')}\n\n`);
    this.tooltip.appendMarkdown(
      this.hasGeneratedFiles
        ? '✓ Configuration files exist'
        : '○ No configuration files found'
    );

    // Add command to generate for this editor
    this.command = {
      command: 'promptrek.generate',
      title: 'Generate for Editor',
      arguments: [editorInfo.name]
    };
  }
}
