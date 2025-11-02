/**
 * PrompTrek CLI Installer and Manager
 *
 * Handles automatic installation and detection of the PrompTrek CLI
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export class CliInstaller {
  private extensionPath: string;
  private outputChannel: vscode.OutputChannel;

  constructor(context: vscode.ExtensionContext, outputChannel: vscode.OutputChannel) {
    this.extensionPath = context.extensionPath;
    this.outputChannel = outputChannel;
  }

  /**
   * Get the bundled CLI path (inside extension)
   */
  private getBundledCliPath(): string {
    return path.join(this.extensionPath, 'bundled', 'promptrek');
  }

  /**
   * Get the user's local CLI installation path
   */
  private getUserCliPath(): string {
    const homeDir = process.env.HOME || process.env.USERPROFILE || '';
    return path.join(homeDir, '.promptrek', 'cli');
  }

  /**
   * Check if PrompTrek CLI is available
   */
  async checkCliAvailable(): Promise<{ available: boolean; path?: string; version?: string }> {
    // Check configured path first
    const config = vscode.workspace.getConfiguration('promptrek');
    const configuredPath = config.get<string>('cliPath') || 'promptrek';

    // Try configured path
    const configured = await this.tryCliPath(configuredPath);
    if (configured.available) {
      return configured;
    }

    // Try bundled CLI
    const bundled = await this.tryCliPath(this.getBundledCliPath());
    if (bundled.available) {
      return bundled;
    }

    // Try user installation
    const userCli = await this.tryCliPath(this.getUserCliPath());
    if (userCli.available) {
      return userCli;
    }

    // Try system PATH
    const system = await this.tryCliPath('promptrek');
    if (system.available) {
      return system;
    }

    return { available: false };
  }

  /**
   * Try to execute CLI at a specific path
   */
  private async tryCliPath(cliPath: string): Promise<{ available: boolean; path?: string; version?: string }> {
    try {
      const { stdout } = await execAsync(`${cliPath} --version`, { timeout: 5000 });
      const version = stdout.trim();
      return {
        available: true,
        path: cliPath,
        version
      };
    } catch (error) {
      return { available: false };
    }
  }

  /**
   * Prompt user to install CLI
   */
  async promptInstallation(): Promise<boolean> {
    const choice = await vscode.window.showInformationMessage(
      'PrompTrek CLI is not installed. Would you like to install it automatically?',
      'Install Now',
      'Install Manually',
      'Cancel'
    );

    if (choice === 'Install Now') {
      return await this.autoInstall();
    } else if (choice === 'Install Manually') {
      this.showManualInstallInstructions();
      return false;
    }

    return false;
  }

  /**
   * Automatically install PrompTrek CLI
   */
  private async autoInstall(): Promise<boolean> {
    return await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: 'Installing PrompTrek CLI...',
        cancellable: false
      },
      async (progress) => {
        try {
          // Check if Python is available
          progress.report({ message: 'Checking Python installation...' });
          const hasPython = await this.checkPython();

          if (!hasPython) {
            vscode.window.showErrorMessage(
              'Python 3.9+ is required to install PrompTrek. Please install Python first.',
              'Download Python'
            ).then(choice => {
              if (choice === 'Download Python') {
                vscode.env.openExternal(vscode.Uri.parse('https://www.python.org/downloads/'));
              }
            });
            return false;
          }

          // Install using pip
          progress.report({ message: 'Installing PrompTrek CLI via pip...', increment: 30 });

          const installPath = this.getUserCliPath();
          await fs.promises.mkdir(path.dirname(installPath), { recursive: true });

          // Try installing from the bundled source or PyPI
          const success = await this.installViaPip(installPath);

          if (success) {
            progress.report({ message: 'Installation complete!', increment: 100 });

            // Update configuration to use installed CLI
            const config = vscode.workspace.getConfiguration('promptrek');
            await config.update('cliPath', installPath, vscode.ConfigurationTarget.Global);

            vscode.window.showInformationMessage(
              '✅ PrompTrek CLI installed successfully!',
              'Test It'
            ).then(choice => {
              if (choice === 'Test It') {
                this.testCli(installPath);
              }
            });

            return true;
          } else {
            this.showManualInstallInstructions();
            return false;
          }
        } catch (error: any) {
          this.outputChannel.appendLine(`Installation error: ${error.message}`);
          vscode.window.showErrorMessage(
            `Failed to install PrompTrek CLI: ${error.message}`,
            'Manual Install'
          ).then(choice => {
            if (choice === 'Manual Install') {
              this.showManualInstallInstructions();
            }
          });
          return false;
        }
      }
    );
  }

  /**
   * Check if Python is available
   */
  private async checkPython(): Promise<boolean> {
    const pythonCommands = ['python3', 'python'];

    for (const cmd of pythonCommands) {
      try {
        const { stdout } = await execAsync(`${cmd} --version`, { timeout: 3000 });
        const version = stdout.trim();
        this.outputChannel.appendLine(`Found ${cmd}: ${version}`);

        // Check if version is 3.9+
        const match = version.match(/Python (\d+)\.(\d+)/);
        if (match) {
          const major = parseInt(match[1]);
          const minor = parseInt(match[2]);
          if (major === 3 && minor >= 9) {
            return true;
          }
        }
      } catch (error) {
        continue;
      }
    }

    return false;
  }

  /**
   * Install PrompTrek using pip
   */
  private async installViaPip(targetPath: string): Promise<boolean> {
    try {
      // Try to find the PrompTrek source directory
      const possiblePaths = [
        path.join(this.extensionPath, '..', '..'),  // Parent of vscode-extension
        path.join(this.extensionPath, 'bundled', 'promptrek-source'),
      ];

      let sourcePath: string | null = null;
      for (const p of possiblePaths) {
        if (fs.existsSync(path.join(p, 'pyproject.toml'))) {
          sourcePath = p;
          break;
        }
      }

      if (sourcePath) {
        this.outputChannel.appendLine(`Installing from source: ${sourcePath}`);

        // Create a virtual environment
        const venvPath = path.join(path.dirname(targetPath), '.venv');
        await execAsync(`python3 -m venv ${venvPath}`, { timeout: 30000 });

        // Activate and install
        const pip = path.join(venvPath, 'bin', 'pip');
        await execAsync(`${pip} install -e "${sourcePath}"`, { timeout: 60000 });

        // Create wrapper script
        const promptrekPath = path.join(venvPath, 'bin', 'promptrek');
        await fs.promises.copyFile(promptrekPath, targetPath);
        await fs.promises.chmod(targetPath, 0o755);

        return true;
      }

      return false;
    } catch (error: any) {
      this.outputChannel.appendLine(`pip install error: ${error.message}`);
      return false;
    }
  }

  /**
   * Test the CLI installation
   */
  private async testCli(cliPath: string): Promise<void> {
    try {
      const { stdout } = await execAsync(`${cliPath} --version`);
      vscode.window.showInformationMessage(`PrompTrek CLI: ${stdout.trim()}`);
    } catch (error: any) {
      vscode.window.showErrorMessage(`CLI test failed: ${error.message}`);
    }
  }

  /**
   * Show manual installation instructions
   */
  private showManualInstallInstructions(): void {
    const instructions = `
# Manual Installation Instructions

## Option 1: Using uv (Recommended)
\`\`\`bash
curl -LsSf https://astral.sh/uv/install.sh | sh
cd /path/to/promptrek
uv sync
source .venv/bin/activate
\`\`\`

## Option 2: Using pip
\`\`\`bash
cd /path/to/promptrek
pip install -e .
\`\`\`

## Option 3: Using uv tool
\`\`\`bash
cd /path/to/promptrek
uv tool install -e .
\`\`\`

After installation, verify with:
\`\`\`bash
promptrek --version
\`\`\`

Then restart VSCode or reload the extension.
`;

    const doc = vscode.workspace.openTextDocument({
      content: instructions,
      language: 'markdown'
    });

    doc.then(d => vscode.window.showTextDocument(d));
  }

  /**
   * Get the CLI path to use for commands
   */
  async getCliPath(): Promise<string | null> {
    const check = await this.checkCliAvailable();

    if (check.available && check.path) {
      return check.path;
    }

    // CLI not available, prompt for installation
    const installed = await this.promptInstallation();

    if (installed) {
      const recheck = await this.checkCliAvailable();
      return recheck.path || null;
    }

    return null;
  }
}
