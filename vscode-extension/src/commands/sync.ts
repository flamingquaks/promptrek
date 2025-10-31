/**
 * Sync command implementation
 */

import * as vscode from 'vscode';
import { PrompTrekCli } from '../utils/promptrekCli';
import { SUPPORTED_EDITORS } from '../types/promptrek';

export async function syncCommand(cli: PrompTrekCli): Promise<void> {
  // Ask for editor to sync from
  const editorChoice = await vscode.window.showQuickPick(
    SUPPORTED_EDITORS.filter(e => e.hasProjectConfig).map(e => ({
      label: e.displayName,
      description: e.description,
      value: e.name
    })),
    {
      placeHolder: 'Select editor to sync from',
      title: 'Sync from Editor Files'
    }
  );

  if (!editorChoice) {
    return;
  }

  // Ask for output file
  const output = await vscode.window.showInputBox({
    prompt: 'Output file name',
    value: 'project.promptrek.yaml',
    placeHolder: 'project.promptrek.yaml'
  });

  if (!output) {
    return;
  }

  // Ask about dry run
  const dryRun = await vscode.window.showQuickPick(['No', 'Yes'], {
    placeHolder: 'Perform a dry run (preview changes without writing)?',
    title: 'Dry Run'
  });

  if (dryRun === undefined) {
    return;
  }

  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: `Syncing from ${editorChoice.label}...`,
      cancellable: false
    },
    async progress => {
      progress.report({ increment: 0 });

      const result = await cli.sync({
        editor: editorChoice.value,
        output,
        dryRun: dryRun === 'Yes'
      });

      if (result.success) {
        if (dryRun === 'Yes') {
          // Show preview
          const doc = await vscode.workspace.openTextDocument({
            content: result.stdout,
            language: 'yaml'
          });
          await vscode.window.showTextDocument(doc, {
            preview: true,
            viewColumn: vscode.ViewColumn.Beside
          });
        } else {
          vscode.window.showInformationMessage(
            `Successfully synced from ${editorChoice.label} to ${output}`
          );

          // Open the synced file
          const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
          if (workspaceRoot) {
            const filePath = vscode.Uri.file(`${workspaceRoot}/${output}`);
            const doc = await vscode.workspace.openTextDocument(filePath);
            await vscode.window.showTextDocument(doc);
          }

          // Refresh tree views
          vscode.commands.executeCommand('promptrek.refresh');
        }
      } else {
        vscode.window.showErrorMessage(
          `Sync failed: ${result.stderr || result.error?.message}`
        );
      }
    }
  );
}
