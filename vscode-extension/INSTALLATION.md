# Installation Guide

## Prerequisites

Before installing the PrompTrek VSCode extension, ensure you have:

1. **Visual Studio Code** 1.85.0 or higher
2. **Node.js** 18.x or higher
3. **PrompTrek CLI** installed and available in your PATH

### Installing PrompTrek CLI

If you haven't installed the PrompTrek CLI yet:

```bash
# Clone the repository
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek

# Install using uv (recommended)
uv sync

# Or install using pip
pip install -e .

# Verify installation
promptrek --version
```

## Development Installation

To install the extension for development:

1. **Clone and navigate to the extension directory:**
   ```bash
   cd promptrek/vscode-extension
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Compile TypeScript:**
   ```bash
   npm run compile
   ```

4. **Open in VSCode:**
   ```bash
   code .
   ```

5. **Launch Extension Development Host:**
   - Press `F5` to start debugging
   - Or use the "Run Extension" configuration from the Run and Debug panel

6. **Test the extension:**
   - Open a workspace in the Extension Development Host
   - The PrompTrek sidebar should appear
   - Try creating a new configuration with `PrompTrek: Initialize Configuration`

## Building VSIX Package

To create a distributable VSIX package:

1. **Install vsce (if not already installed):**
   ```bash
   npm install -g @vscode/vsce
   ```

2. **Build the VSIX:**
   ```bash
   cd vscode-extension
   npm run compile
   vsce package
   ```

3. **Install the VSIX:**
   ```bash
   code --install-extension promptrek-vscode-0.1.0.vsix
   ```

## Configuration

After installation, configure the extension:

1. **Open VSCode Settings** (`Ctrl+,` / `Cmd+,`)

2. **Search for "PrompTrek"**

3. **Configure settings:**
   ```json
   {
     "promptrek.cliPath": "promptrek",
     "promptrek.autoValidate": true,
     "promptrek.defaultSchemaVersion": "3.1.0",
     "promptrek.showStatusBar": true
   }
   ```

### Setting Custom CLI Path

If PrompTrek is not in your PATH, specify the full path:

**Windows:**
```json
{
  "promptrek.cliPath": "C:\\Users\\YourName\\promptrek\\promptrek"
}
```

**macOS/Linux:**
```json
{
  "promptrek.cliPath": "/home/username/promptrek/promptrek"
}
```

## Troubleshooting

### Extension Not Activating

1. Check the VSCode Developer Console:
   - Help → Toggle Developer Tools
   - Look for errors in the Console tab

2. Verify PrompTrek CLI is accessible:
   ```bash
   which promptrek  # Unix/Mac
   where promptrek  # Windows
   ```

3. Try reloading VSCode:
   - `Ctrl+Shift+P` / `Cmd+Shift+P`
   - Type "Developer: Reload Window"

### Commands Not Working

1. Check the PrompTrek output channel:
   - View → Output
   - Select "PrompTrek" from dropdown
   - Look for error messages

2. Verify CLI path in settings:
   ```bash
   promptrek --version
   ```

3. Try running commands manually:
   ```bash
   cd your-workspace
   promptrek validate project.promptrek.yaml
   ```

### Tree Views Not Showing Configuration

1. Ensure you have a `.promptrek.yaml` file in your workspace
2. Click the refresh button in the PrompTrek sidebar
3. Try running `PrompTrek: Refresh View` command

## Updating

### Development Version

```bash
cd promptrek/vscode-extension
git pull
npm install
npm run compile
```

Then press `F5` to reload the extension.

### Installed VSIX

1. Uninstall the old version:
   ```bash
   code --uninstall-extension flamingquaks.promptrek-vscode
   ```

2. Install the new version:
   ```bash
   code --install-extension promptrek-vscode-0.1.0.vsix
   ```

## Next Steps

Once installed:

1. **Read the README**: Check out [README.md](./README.md) for features and usage
2. **Create a configuration**: Use `PrompTrek: Initialize Configuration`
3. **Explore examples**: Look at the [examples directory](../examples/)
4. **Join the community**: Visit the [GitHub repository](https://github.com/flamingquaks/promptrek)

## Getting Help

- **Documentation**: https://flamingquaks.github.io/promptrek
- **Issues**: https://github.com/flamingquaks/promptrek/issues
- **Discussions**: https://github.com/flamingquaks/promptrek/discussions
