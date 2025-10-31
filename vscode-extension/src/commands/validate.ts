/**
 * Validate command implementation
 */

import * as vscode from 'vscode';
import { PrompTrekCli } from '../utils/promptrekCli';
import { YamlParser } from '../utils/yamlParser';

export async function validateCommand(
  cli: PrompTrekCli,
  fileUri?: vscode.Uri
): Promise<void> {
  let targetFile: vscode.Uri | null = fileUri || null;

  // If no file provided, use primary config
  if (!targetFile) {
    targetFile = await YamlParser.getPrimaryConfigFile();
  }

  if (!targetFile) {
    vscode.window.showErrorMessage('No PrompTrek configuration file found');
    return;
  }

  // Ask about strict mode
  const strict = await vscode.window.showQuickPick(['No', 'Yes'], {
    placeHolder: 'Use strict mode (treat warnings as errors)?',
    title: 'Validation Mode'
  });

  if (strict === undefined) {
    return;
  }

  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: 'Validating PrompTrek configuration...',
      cancellable: false
    },
    async progress => {
      progress.report({ increment: 0 });

      const result = await cli.validate(targetFile!.fsPath, strict === 'Yes');

      if (result.success) {
        vscode.window.showInformationMessage(
          '✓ Configuration is valid',
          'View Output'
        ).then(selection => {
          if (selection === 'View Output') {
            vscode.commands.executeCommand('promptrek.showOutput');
          }
        });
      } else {
        const errorMessage = result.stderr || result.stdout || result.error?.message || 'Unknown error';
        vscode.window.showErrorMessage(
          `Validation failed: ${errorMessage}`,
          'View Output'
        ).then(selection => {
          if (selection === 'View Output') {
            vscode.commands.executeCommand('promptrek.showOutput');
          }
        });
      }
    }
  );
}
