/**
 * Preview command implementation
 */

import * as vscode from 'vscode';
import { PrompTrekCli } from '../utils/promptrekCli';
import { YamlParser } from '../utils/yamlParser';
import { SUPPORTED_EDITORS } from '../types/promptrek';

export async function previewCommand(cli: PrompTrekCli): Promise<void> {
  // Find config file
  const configFile = await YamlParser.getPrimaryConfigFile();
  if (!configFile) {
    vscode.window.showErrorMessage('No PrompTrek configuration file found');
    return;
  }

  // Ask for editor
  const editorChoice = await vscode.window.showQuickPick(
    SUPPORTED_EDITORS.map(e => ({
      label: e.displayName,
      description: e.description,
      value: e.name
    })),
    {
      placeHolder: 'Select editor to preview',
      title: 'Preview Output'
    }
  );

  if (!editorChoice) {
    return;
  }

  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: `Generating preview for ${editorChoice.label}...`,
      cancellable: false
    },
    async progress => {
      progress.report({ increment: 0 });

      const result = await cli.preview({
        file: configFile.fsPath,
        editor: editorChoice.value
      });

      if (result.success) {
        // Show preview in a new document
        const doc = await vscode.workspace.openTextDocument({
          content: result.stdout,
          language: 'markdown'
        });
        await vscode.window.showTextDocument(doc, {
          preview: true,
          viewColumn: vscode.ViewColumn.Beside
        });
      } else {
        vscode.window.showErrorMessage(
          `Preview failed: ${result.stderr || result.error?.message}`
        );
      }
    }
  );
}
