/**
 * PrompTrek CLI wrapper for VSCode extension
 */

import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export interface CliResult {
  success: boolean;
  stdout: string;
  stderr: string;
  error?: Error;
}

export class PrompTrekCli {
  private cliPath: string;
  private outputChannel: vscode.OutputChannel;

  constructor(outputChannel: vscode.OutputChannel) {
    this.outputChannel = outputChannel;
    const config = vscode.workspace.getConfiguration('promptrek');
    this.cliPath = config.get<string>('cliPath') || 'promptrek';
  }

  /**
   * Execute a PrompTrek CLI command
   */
  private async execute(args: string[], cwd?: string): Promise<CliResult> {
    const command = `${this.cliPath} ${args.join(' ')}`;
    this.outputChannel.appendLine(`> ${command}`);

    try {
      const { stdout, stderr } = await execAsync(command, {
        cwd: cwd || vscode.workspace.workspaceFolders?.[0]?.uri.fsPath
      });

      this.outputChannel.appendLine(stdout);
      if (stderr) {
        this.outputChannel.appendLine(`stderr: ${stderr}`);
      }

      return {
        success: true,
        stdout,
        stderr
      };
    } catch (error: any) {
      this.outputChannel.appendLine(`Error: ${error.message}`);
      if (error.stdout) {
        this.outputChannel.appendLine(error.stdout);
      }
      if (error.stderr) {
        this.outputChannel.appendLine(error.stderr);
      }

      return {
        success: false,
        stdout: error.stdout || '',
        stderr: error.stderr || '',
        error
      };
    }
  }

  /**
   * Initialize a new PrompTrek configuration
   */
  async init(options: {
    template?: string;
    output: string;
    schemaVersion?: string;
    setupHooks?: boolean;
  }): Promise<CliResult> {
    const args = ['init'];

    if (options.template) {
      args.push('--template', options.template);
    }
    if (options.output) {
      args.push('--output', options.output);
    }
    if (options.schemaVersion) {
      args.push(`--v${options.schemaVersion.split('.')[0]}`);
    }
    if (options.setupHooks) {
      args.push('--setup-hooks');
    }

    return this.execute(args);
  }

  /**
   * Validate a PrompTrek configuration file
   */
  async validate(filePath: string, strict: boolean = false): Promise<CliResult> {
    const args = ['validate', filePath];
    if (strict) {
      args.push('--strict');
    }
    return this.execute(args);
  }

  /**
   * Generate editor-specific files
   */
  async generate(options: {
    file: string;
    editor?: string;
    all?: boolean;
    dryRun?: boolean;
    variables?: Record<string, string>;
    headless?: boolean;
  }): Promise<CliResult> {
    const args = ['generate', options.file];

    if (options.editor) {
      args.push('--editor', options.editor);
    }
    if (options.all) {
      args.push('--all');
    }
    if (options.dryRun) {
      args.push('--dry-run');
    }
    if (options.headless) {
      args.push('--headless');
    }
    if (options.variables) {
      for (const [key, value] of Object.entries(options.variables)) {
        args.push('-V', `${key}=${value}`);
      }
    }

    return this.execute(args);
  }

  /**
   * Preview output for an editor
   */
  async preview(options: {
    file: string;
    editor: string;
    variables?: Record<string, string>;
  }): Promise<CliResult> {
    const args = ['preview', options.file, '--editor', options.editor];

    if (options.variables) {
      for (const [key, value] of Object.entries(options.variables)) {
        args.push('-V', `${key}=${value}`);
      }
    }

    return this.execute(args);
  }

  /**
   * Sync from editor files to PrompTrek format
   */
  async sync(options: {
    editor: string;
    sourceDir?: string;
    output?: string;
    dryRun?: boolean;
    force?: boolean;
  }): Promise<CliResult> {
    const args = ['sync', '--editor', options.editor];

    if (options.sourceDir) {
      args.push('--source-dir', options.sourceDir);
    }
    if (options.output) {
      args.push('--output', options.output);
    }
    if (options.dryRun) {
      args.push('--dry-run');
    }
    if (options.force) {
      args.push('--force');
    }

    return this.execute(args);
  }

  /**
   * Migrate schema version
   */
  async migrate(options: {
    inputFile: string;
    output?: string;
    force?: boolean;
  }): Promise<CliResult> {
    const args = ['migrate', options.inputFile];

    if (options.output) {
      args.push('--output', options.output);
    }
    if (options.force) {
      args.push('--force');
    }

    return this.execute(args);
  }

  /**
   * List plugins in a configuration
   */
  async listPlugins(file?: string): Promise<CliResult> {
    const args = ['plugins', 'list'];
    if (file) {
      args.push('--file', file);
    }
    return this.execute(args);
  }

  /**
   * Generate plugins for an editor
   */
  async generatePlugins(options: {
    file?: string;
    editor: string;
    dryRun?: boolean;
    yes?: boolean;
  }): Promise<CliResult> {
    const args = ['plugins', 'generate', '--editor', options.editor];

    if (options.file) {
      args.push('--file', options.file);
    }
    if (options.dryRun) {
      args.push('--dry-run');
    }
    if (options.yes) {
      args.push('--yes');
    }

    return this.execute(args);
  }

  /**
   * Install pre-commit hooks
   */
  async installHooks(options: {
    activate?: boolean;
    force?: boolean;
  }): Promise<CliResult> {
    const args = ['install-hooks'];

    if (options.activate) {
      args.push('--activate');
    }
    if (options.force) {
      args.push('--force');
    }

    return this.execute(args);
  }

  /**
   * Configure .gitignore
   */
  async configIgnores(options: {
    removeCached?: boolean;
    dryRun?: boolean;
  }): Promise<CliResult> {
    const args = ['config-ignores'];

    if (options.removeCached) {
      args.push('--remove-cached');
    }
    if (options.dryRun) {
      args.push('--dry-run');
    }

    return this.execute(args);
  }

  /**
   * List supported editors
   */
  async listEditors(): Promise<CliResult> {
    return this.execute(['list-editors']);
  }
}
