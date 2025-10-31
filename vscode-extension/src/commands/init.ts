/**
 * Initialize command implementation
 */

import * as vscode from 'vscode';
import { PrompTrekCli } from '../utils/promptrekCli';

export async function initCommand(cli: PrompTrekCli): Promise<void> {
  // Ask for configuration details
  const output = await vscode.window.showInputBox({
    prompt: 'Output file name',
    value: 'project.promptrek.yaml',
    placeHolder: 'project.promptrek.yaml'
  });

  if (!output) {
    return;
  }

  // Ask for schema version
  const schemaVersion = await vscode.window.showQuickPick(
    [
      { label: 'v3.1.0', description: 'Latest (Recommended)', value: '3.1.0' },
      { label: 'v3.0.0', description: 'Current stable', value: '3.0.0' },
      { label: 'v2.1.0', description: 'Legacy with plugins', value: '2.1.0' },
      { label: 'v2.0.0', description: 'Legacy markdown', value: '2.0.0' },
      { label: 'v1.0.0', description: 'Original structured format', value: '1.0.0' }
    ],
    {
      placeHolder: 'Select schema version',
      title: 'PrompTrek Schema Version'
    }
  );

  if (!schemaVersion) {
    return;
  }

  // Ask about template
  const useTemplate = await vscode.window.showQuickPick(
    [
      { label: 'No template', description: 'Start with empty configuration', value: '' },
      { label: 'React', description: 'React TypeScript project', value: 'react' },
      { label: 'Node', description: 'Node.js API service', value: 'node' },
      { label: 'Python', description: 'Python project', value: 'python' }
    ],
    {
      placeHolder: 'Select a template (optional)',
      title: 'Project Template'
    }
  );

  if (!useTemplate) {
    return;
  }

  // Ask about pre-commit hooks
  const setupHooks = await vscode.window.showQuickPick(
    [
      { label: 'Yes', description: 'Set up pre-commit hooks automatically', value: true },
      { label: 'No', description: 'Skip hook setup', value: false }
    ],
    {
      placeHolder: 'Set up pre-commit hooks?',
      title: 'Pre-commit Hooks'
    }
  );

  if (setupHooks === undefined) {
    return;
  }

  // Show progress
  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: 'Initializing PrompTrek configuration...',
      cancellable: false
    },
    async progress => {
      progress.report({ increment: 0 });

      const result = await cli.init({
        output,
        schemaVersion: schemaVersion.value,
        template: useTemplate.value || undefined,
        setupHooks: setupHooks.value
      });

      if (result.success) {
        vscode.window.showInformationMessage(
          `PrompTrek configuration created: ${output}`
        );

        // Open the created file
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (workspaceRoot) {
          const filePath = vscode.Uri.file(`${workspaceRoot}/${output}`);
          const doc = await vscode.workspace.openTextDocument(filePath);
          await vscode.window.showTextDocument(doc);
        }

        // Trigger refresh of tree views
        vscode.commands.executeCommand('promptrek.refresh');
      } else {
        vscode.window.showErrorMessage(
          `Failed to initialize configuration: ${result.stderr || result.error?.message}`
        );
      }
    }
  );
}
