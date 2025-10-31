/**
 * Generate command implementation
 */

import * as vscode from 'vscode';
import { PrompTrekCli } from '../utils/promptrekCli';
import { YamlParser } from '../utils/yamlParser';
import { SUPPORTED_EDITORS } from '../types/promptrek';

export async function generateCommand(
  cli: PrompTrekCli,
  preselectedEditor?: string
): Promise<void> {
  // Find config file
  const configFile = await YamlParser.getPrimaryConfigFile();
  if (!configFile) {
    const create = await vscode.window.showInformationMessage(
      'No PrompTrek configuration found. Would you like to create one?',
      'Yes',
      'No'
    );

    if (create === 'Yes') {
      await vscode.commands.executeCommand('promptrek.init');
    }
    return;
  }

  let editor: string | undefined = preselectedEditor;

  // If no editor preselected, ask user to select
  if (!editor) {
    const editorChoice = await vscode.window.showQuickPick(
      [
        ...SUPPORTED_EDITORS.map(e => ({
          label: e.displayName,
          description: e.description,
          value: e.name
        })),
        {
          label: 'All Editors',
          description: 'Generate for all supported editors',
          value: 'all'
        }
      ],
      {
        placeHolder: 'Select target editor',
        title: 'Generate PrompTrek Configuration'
      }
    );

    if (!editorChoice) {
      return;
    }

    editor = editorChoice.value;
  }

  // Ask for variable overrides (optional)
  const addVariables = await vscode.window.showQuickPick(['Yes', 'No'], {
    placeHolder: 'Override any variables?',
    title: 'Variable Overrides'
  });

  let variables: Record<string, string> | undefined;

  if (addVariables === 'Yes') {
    variables = {};
    let addMore = true;

    while (addMore) {
      const varInput = await vscode.window.showInputBox({
        prompt: 'Enter variable (KEY=value) or leave empty to finish',
        placeHolder: 'VARIABLE_NAME=value'
      });

      if (!varInput) {
        addMore = false;
      } else if (varInput.includes('=')) {
        const [key, ...valueParts] = varInput.split('=');
        variables[key.trim()] = valueParts.join('=').trim();
      } else {
        vscode.window.showWarningMessage('Invalid format. Use KEY=value');
      }
    }
  }

  // Ask about headless mode
  const headless = await vscode.window.showQuickPick(['No', 'Yes'], {
    placeHolder: 'Generate with headless agent instructions?',
    title: 'Headless Mode'
  });

  // Show progress
  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: `Generating for ${editor === 'all' ? 'all editors' : editor}...`,
      cancellable: false
    },
    async progress => {
      progress.report({ increment: 0 });

      const result = await cli.generate({
        file: configFile.fsPath,
        editor: editor === 'all' ? undefined : editor,
        all: editor === 'all',
        variables,
        headless: headless === 'Yes'
      });

      if (result.success) {
        vscode.window.showInformationMessage(
          `Successfully generated configuration for ${editor === 'all' ? 'all editors' : editor}`
        );

        // Refresh tree views
        vscode.commands.executeCommand('promptrek.refresh');
      } else {
        vscode.window.showErrorMessage(
          `Failed to generate: ${result.stderr || result.error?.message}`
        );
      }
    }
  );
}

export async function generateAllCommand(cli: PrompTrekCli): Promise<void> {
  return generateCommand(cli, 'all');
}
