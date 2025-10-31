/**
 * PrompTrek VSCode Extension
 *
 * Provides a visual interface for managing PrompTrek configurations
 */

import * as vscode from 'vscode';
import { PrompTrekCli } from './utils/promptrekCli';
import { YamlParser } from './utils/yamlParser';
import { ConfigExplorerProvider } from './views/configExplorer';
import { EditorStatusProvider } from './views/editorStatusView';
import { initCommand } from './commands/init';
import { generateCommand, generateAllCommand } from './commands/generate';
import { validateCommand } from './commands/validate';
import { previewCommand } from './commands/preview';
import { syncCommand } from './commands/sync';

let outputChannel: vscode.OutputChannel;
let cli: PrompTrekCli;
let configExplorer: ConfigExplorerProvider;
let editorStatusProvider: EditorStatusProvider;
let statusBarItem: vscode.StatusBarItem;

export function activate(context: vscode.ExtensionContext) {
  console.log('PrompTrek extension is now active');

  // Create output channel
  outputChannel = vscode.window.createOutputChannel('PrompTrek');
  context.subscriptions.push(outputChannel);

  // Initialize CLI wrapper
  cli = new PrompTrekCli(outputChannel);

  // Create tree view providers
  configExplorer = new ConfigExplorerProvider();
  editorStatusProvider = new EditorStatusProvider();

  // Register tree views
  const configTreeView = vscode.window.createTreeView('promptrek-config', {
    treeDataProvider: configExplorer,
    showCollapseAll: true
  });

  const editorTreeView = vscode.window.createTreeView('promptrek-editors', {
    treeDataProvider: editorStatusProvider,
    showCollapseAll: false
  });

  context.subscriptions.push(configTreeView, editorTreeView);

  // Create status bar item
  statusBarItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Right,
    100
  );
  statusBarItem.command = 'promptrek.openConfig';
  context.subscriptions.push(statusBarItem);

  // Update status bar
  updateStatusBar();

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand('promptrek.init', () => initCommand(cli)),

    vscode.commands.registerCommand('promptrek.validate', (uri?: vscode.Uri) =>
      validateCommand(cli, uri)
    ),

    vscode.commands.registerCommand('promptrek.generate', (editorName?: string) =>
      generateCommand(cli, editorName)
    ),

    vscode.commands.registerCommand('promptrek.generateAll', () =>
      generateAllCommand(cli)
    ),

    vscode.commands.registerCommand('promptrek.preview', () => previewCommand(cli)),

    vscode.commands.registerCommand('promptrek.sync', () => syncCommand(cli)),

    vscode.commands.registerCommand('promptrek.migrate', async () => {
      const configFile = await YamlParser.getPrimaryConfigFile();
      if (!configFile) {
        vscode.window.showErrorMessage('No PrompTrek configuration file found');
        return;
      }

      const output = await vscode.window.showInputBox({
        prompt: 'Output file name (leave empty for in-place migration)',
        placeHolder: 'migrated.promptrek.yaml'
      });

      const result = await cli.migrate({
        inputFile: configFile.fsPath,
        output: output || undefined,
        force: true
      });

      if (result.success) {
        vscode.window.showInformationMessage('Configuration migrated successfully');
        vscode.commands.executeCommand('promptrek.refresh');
      } else {
        vscode.window.showErrorMessage(`Migration failed: ${result.stderr}`);
      }
    }),

    vscode.commands.registerCommand('promptrek.refresh', () => {
      configExplorer.refresh();
      editorStatusProvider.refresh();
      updateStatusBar();
    }),

    vscode.commands.registerCommand('promptrek.openConfig', async () => {
      const configFile = await YamlParser.getPrimaryConfigFile();
      if (configFile) {
        const doc = await vscode.workspace.openTextDocument(configFile);
        await vscode.window.showTextDocument(doc);
      } else {
        const create = await vscode.window.showInformationMessage(
          'No PrompTrek configuration found. Would you like to create one?',
          'Yes',
          'No'
        );
        if (create === 'Yes') {
          vscode.commands.executeCommand('promptrek.init');
        }
      }
    }),

    vscode.commands.registerCommand('promptrek.openConfigEditor', async () => {
      vscode.window.showInformationMessage(
        'Configuration editor webview coming soon! For now, use the text editor.'
      );
    }),

    vscode.commands.registerCommand('promptrek.installHooks', async () => {
      const activate = await vscode.window.showQuickPick(['Yes', 'No'], {
        placeHolder: 'Activate hooks in git after installation?',
        title: 'Activate Hooks'
      });

      if (activate === undefined) {
        return;
      }

      const result = await cli.installHooks({
        activate: activate === 'Yes',
        force: false
      });

      if (result.success) {
        vscode.window.showInformationMessage('Pre-commit hooks installed successfully');
      } else {
        vscode.window.showErrorMessage(`Failed to install hooks: ${result.stderr}`);
      }
    }),

    vscode.commands.registerCommand('promptrek.configIgnores', async () => {
      const removeCached = await vscode.window.showQuickPick(['No', 'Yes'], {
        placeHolder: 'Remove already-committed files from git cache?',
        title: 'Remove Cached Files'
      });

      if (removeCached === undefined) {
        return;
      }

      const result = await cli.configIgnores({
        removeCached: removeCached === 'Yes',
        dryRun: false
      });

      if (result.success) {
        vscode.window.showInformationMessage('.gitignore configured successfully');
      } else {
        vscode.window.showErrorMessage(`Failed to configure .gitignore: ${result.stderr}`);
      }
    }),

    vscode.commands.registerCommand('promptrek.listPlugins', async () => {
      const configFile = await YamlParser.getPrimaryConfigFile();
      const result = await cli.listPlugins(configFile?.fsPath);

      if (result.success) {
        const doc = await vscode.workspace.openTextDocument({
          content: result.stdout,
          language: 'plaintext'
        });
        await vscode.window.showTextDocument(doc, { preview: true });
      } else {
        vscode.window.showErrorMessage(`Failed to list plugins: ${result.stderr}`);
      }
    }),

    vscode.commands.registerCommand('promptrek.generatePlugins', async () => {
      const configFile = await YamlParser.getPrimaryConfigFile();
      if (!configFile) {
        vscode.window.showErrorMessage('No PrompTrek configuration file found');
        return;
      }

      const editorChoice = await vscode.window.showQuickPick(
        [
          'claude', 'cursor', 'continue', 'windsurf', 'cline',
          'amazon-q', 'kiro', 'all'
        ],
        {
          placeHolder: 'Select editor for plugin generation',
          title: 'Generate Plugins'
        }
      );

      if (!editorChoice) {
        return;
      }

      const result = await cli.generatePlugins({
        file: configFile.fsPath,
        editor: editorChoice,
        yes: true
      });

      if (result.success) {
        vscode.window.showInformationMessage(
          `Plugins generated successfully for ${editorChoice}`
        );
        vscode.commands.executeCommand('promptrek.refresh');
      } else {
        vscode.window.showErrorMessage(`Plugin generation failed: ${result.stderr}`);
      }
    }),

    vscode.commands.registerCommand('promptrek.showOutput', () => {
      outputChannel.show();
    })
  );

  // Watch for .promptrek.yaml file changes
  const fileWatcher = vscode.workspace.createFileSystemWatcher('**/*.promptrek.yaml');

  fileWatcher.onDidChange(() => {
    vscode.commands.executeCommand('promptrek.refresh');
  });

  fileWatcher.onDidCreate(() => {
    vscode.commands.executeCommand('promptrek.refresh');
  });

  fileWatcher.onDidDelete(() => {
    vscode.commands.executeCommand('promptrek.refresh');
  });

  context.subscriptions.push(fileWatcher);

  // Auto-validate on save if enabled
  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument(async document => {
      const config = vscode.workspace.getConfiguration('promptrek');
      const autoValidate = config.get<boolean>('autoValidate');

      if (autoValidate && document.fileName.endsWith('.promptrek.yaml')) {
        await validateCommand(cli, document.uri);
      }
    })
  );

  // Show welcome message on first activation
  const isFirstActivation = context.globalState.get('promptrek.firstActivation', true);
  if (isFirstActivation) {
    vscode.window
      .showInformationMessage(
        'Welcome to PrompTrek! Manage your AI editor configurations with ease.',
        'Get Started',
        'View Docs'
      )
      .then(selection => {
        if (selection === 'Get Started') {
          vscode.commands.executeCommand('promptrek.init');
        } else if (selection === 'View Docs') {
          vscode.env.openExternal(
            vscode.Uri.parse('https://flamingquaks.github.io/promptrek')
          );
        }
      });

    context.globalState.update('promptrek.firstActivation', false);
  }
}

async function updateStatusBar() {
  const config = vscode.workspace.getConfiguration('promptrek');
  const showStatusBar = config.get<boolean>('showStatusBar');

  if (!showStatusBar) {
    statusBarItem.hide();
    return;
  }

  const configFile = await YamlParser.getPrimaryConfigFile();

  if (configFile) {
    const configData = await YamlParser.parseFile(configFile.fsPath);
    if (configData) {
      statusBarItem.text = `$(file) PrompTrek v${configData.schema_version}`;
      statusBarItem.tooltip = `PrompTrek Configuration\nSchema: ${configData.schema_version}\nFile: ${configFile.fsPath}`;
      statusBarItem.show();
    } else {
      statusBarItem.hide();
    }
  } else {
    statusBarItem.text = '$(file) PrompTrek';
    statusBarItem.tooltip = 'No PrompTrek configuration found. Click to create one.';
    statusBarItem.show();
  }
}

export function deactivate() {
  console.log('PrompTrek extension deactivated');
}
