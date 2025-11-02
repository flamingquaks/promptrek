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
      'PrompTrek CLI is not installed. Would you like to install it automatically? (Installation logs will appear in the Output panel)',
      'Install Now',
      'Install Manually',
      'Cancel'
    );

    if (choice === 'Install Now') {
      const result = await this.autoInstall();
      if (!result) {
        // Show output panel if installation failed
        this.outputChannel.show(true);
      }
      return result;
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
    // Show output channel so users can see what's happening
    this.outputChannel.show(true);

    return await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: 'Installing PrompTrek CLI...',
        cancellable: false
      },
      async (progress) => {
        try {
          this.outputChannel.appendLine('\n========================================');
          this.outputChannel.appendLine('PrompTrek CLI Auto-Installation Started');
          this.outputChannel.appendLine('========================================\n');

          // Check if Python is available
          progress.report({ message: 'Checking Python installation...' });
          this.outputChannel.appendLine('Step 1: Checking Python installation...');

          const hasPython = await this.checkPython();

          if (!hasPython) {
            this.outputChannel.appendLine('✗ Python 3.9+ not found');
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

          this.outputChannel.appendLine('✓ Python 3.9+ found\n');

          // Install using pip
          progress.report({ message: 'Installing PrompTrek CLI via pip...', increment: 30 });
          this.outputChannel.appendLine('Step 2: Installing PrompTrek CLI via pip...');

          const installPath = this.getUserCliPath();
          this.outputChannel.appendLine(`Target installation path: ${installPath}\n`);

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
      this.outputChannel.appendLine('=== Starting PrompTrek Installation ===');

      // Determine platform-specific paths
      const isWindows = process.platform === 'win32';
      const binDir = isWindows ? 'Scripts' : 'bin';
      const pipExe = isWindows ? 'pip.exe' : 'pip';
      const promptrekExe = isWindows ? 'promptrek.exe' : 'promptrek';
      const pythonCmd = isWindows ? 'python' : 'python3';

      // Try to find the PrompTrek source directory
      this.outputChannel.appendLine(`Extension path: ${this.extensionPath}`);
      const possiblePaths = [
        path.join(this.extensionPath, '..', '..'),  // Parent of vscode-extension
        path.join(this.extensionPath, '..'),  // Try one level up too
        path.join(this.extensionPath, 'bundled', 'promptrek-source'),
      ];

      let sourcePath: string | null = null;
      for (const p of possiblePaths) {
        const resolvedPath = path.resolve(p);
        const pyprojectPath = path.join(resolvedPath, 'pyproject.toml');
        this.outputChannel.appendLine(`Checking: ${pyprojectPath}`);

        if (fs.existsSync(pyprojectPath)) {
          sourcePath = resolvedPath;
          this.outputChannel.appendLine(`✓ Found PrompTrek source at: ${sourcePath}`);
          break;
        }
      }

      if (!sourcePath) {
        this.outputChannel.appendLine('✗ Could not find PrompTrek source directory (no pyproject.toml found)');
        this.outputChannel.appendLine('Checked paths:');
        possiblePaths.forEach(p => this.outputChannel.appendLine(`  - ${path.resolve(p)}`));
        return false;
      }

      // Create installation directory
      const installDir = path.dirname(targetPath);
      this.outputChannel.appendLine(`Installation directory: ${installDir}`);

      if (!fs.existsSync(installDir)) {
        this.outputChannel.appendLine('Creating installation directory...');
        await fs.promises.mkdir(installDir, { recursive: true });
      }

      // Create a virtual environment
      const venvPath = path.join(installDir, '.venv');
      this.outputChannel.appendLine(`Creating virtual environment at: ${venvPath}`);

      try {
        const { stdout: venvOut, stderr: venvErr } = await execAsync(
          `${pythonCmd} -m venv "${venvPath}"`,
          { timeout: 30000 }
        );
        if (venvOut) this.outputChannel.appendLine(venvOut);
        if (venvErr) this.outputChannel.appendLine(venvErr);
        this.outputChannel.appendLine('✓ Virtual environment created');
      } catch (venvError: any) {
        this.outputChannel.appendLine(`✗ Failed to create venv: ${venvError.message}`);
        if (venvError.stdout) this.outputChannel.appendLine(`stdout: ${venvError.stdout}`);
        if (venvError.stderr) this.outputChannel.appendLine(`stderr: ${venvError.stderr}`);
        throw venvError;
      }

      // Install PrompTrek
      const pip = path.join(venvPath, binDir, pipExe);
      this.outputChannel.appendLine(`Installing PrompTrek using: ${pip}`);
      this.outputChannel.appendLine(`Install command: ${pip} install -e "${sourcePath}"`);

      try {
        const { stdout: installOut, stderr: installErr } = await execAsync(
          `"${pip}" install -e "${sourcePath}"`,
          { timeout: 120000 }  // Increased timeout for installation
        );
        if (installOut) this.outputChannel.appendLine(installOut);
        if (installErr) this.outputChannel.appendLine(installErr);
        this.outputChannel.appendLine('✓ PrompTrek installed');
      } catch (installError: any) {
        this.outputChannel.appendLine(`✗ Failed to install PrompTrek: ${installError.message}`);
        if (installError.stdout) this.outputChannel.appendLine(`stdout: ${installError.stdout}`);
        if (installError.stderr) this.outputChannel.appendLine(`stderr: ${installError.stderr}`);
        throw installError;
      }

      // Find the promptrek executable
      const promptrekPath = path.join(venvPath, binDir, promptrekExe);
      this.outputChannel.appendLine(`Looking for PrompTrek CLI at: ${promptrekPath}`);

      if (!fs.existsSync(promptrekPath)) {
        this.outputChannel.appendLine(`✗ PrompTrek CLI not found at expected location`);
        this.outputChannel.appendLine(`Checking venv ${binDir} directory contents:`);
        const binContents = await fs.promises.readdir(path.join(venvPath, binDir));
        binContents.forEach(file => this.outputChannel.appendLine(`  - ${file}`));
        return false;
      }

      this.outputChannel.appendLine('✓ PrompTrek CLI found');

      // Copy to target location
      this.outputChannel.appendLine(`Copying CLI to: ${targetPath}`);
      await fs.promises.copyFile(promptrekPath, targetPath);

      if (!isWindows) {
        await fs.promises.chmod(targetPath, 0o755);
      }

      this.outputChannel.appendLine('✓ Installation complete!');
      this.outputChannel.appendLine('=== Installation Summary ===');
      this.outputChannel.appendLine(`Source: ${sourcePath}`);
      this.outputChannel.appendLine(`CLI installed at: ${targetPath}`);

      return true;
    } catch (error: any) {
      this.outputChannel.appendLine(`✗ Installation failed: ${error.message}`);
      if (error.stack) {
        this.outputChannel.appendLine(`Stack trace: ${error.stack}`);
      }
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
