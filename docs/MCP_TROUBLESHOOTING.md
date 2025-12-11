# MCP Configuration Troubleshooting

## "Unexpected end of JSON input" Error - Quick Fix

### Immediate Solutions

1. **Validate JSON Syntax**
   - Open `.kiro/settings/mcp.json` in a JSON validator
   - Check for missing braces, brackets, or commas
   - Ensure no trailing commas (JSON doesn't allow them)

2. **Check File Integrity**
   ```bash
   # On Windows (PowerShell)
   Get-Content .kiro/settings/mcp.json | ConvertFrom-Json
   
   # On Linux/Mac
   cat .kiro/settings/mcp.json | jq .
   ```

3. **Restore from Backup**
   ```bash
   # Copy the backup file
   copy .kiro\settings\mcp.json.backup .kiro\settings\mcp.json
   ```

4. **Recreate Minimal Configuration**
   If the file is corrupted, start with a minimal config:
   
   ```json
   {
     "mcpServers": {}
   }
   ```

### Common Causes

#### 1. Empty File
**Symptom**: File exists but has 0 bytes
**Fix**: Restore from backup or recreate

#### 2. Incomplete JSON
**Symptom**: File ends abruptly
**Fix**: Add missing closing braces/brackets

#### 3. Encoding Issues
**Symptom**: File contains invalid characters
**Fix**: Save as UTF-8 without BOM

#### 4. File Lock
**Symptom**: File is being written by another process
**Fix**: Close other applications, restart Kiro

### Validation Steps

1. **Check file exists**:
   ```bash
   dir .kiro\settings\mcp.json
   ```

2. **Check file size**:
   ```bash
   # Should be > 0 bytes
   (Get-Item .kiro\settings\mcp.json).length
   ```

3. **Validate JSON**:
   ```bash
   # Using Node.js
   node -e "console.log(JSON.parse(require('fs').readFileSync('.kiro/settings/mcp.json', 'utf8')))"
   ```

4. **Check permissions**:
   ```bash
   # Ensure you have read access
   Get-Acl .kiro\settings\mcp.json
   ```

### Prevention

1. **Always validate before saving**
2. **Keep backups** (automatic backup created at `.kiro/settings/mcp.json.backup`)
3. **Use a JSON editor** with syntax validation
4. **Version control** your configuration

### Quick Test Configuration

Use this minimal configuration to test if MCP is working:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "${workspaceFolder}"
      ],
      "env": {},
      "disabled": false,
      "autoApprove": ["read_file"]
    }
  }
}
```

### Reconnecting MCP Servers

After fixing the configuration:

1. **Via Command Palette**:
   - Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
   - Type "MCP: Reconnect Servers"
   - Select the command

2. **Via MCP Server View**:
   - Open the Kiro feature panel
   - Navigate to MCP Servers section
   - Click reconnect icon for each server

3. **Restart Kiro**:
   - Close and reopen Kiro
   - Servers will reconnect automatically

### Getting Help

If the issue persists:

1. Check the Kiro output panel for detailed error messages
2. Look for MCP-related logs
3. Try disabling all servers and enabling them one by one
4. Check if Node.js and npx are properly installed:
   ```bash
   node --version
   npx --version
   ```

### Example: Working Configuration

Here's a complete, validated configuration you can use:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "${workspaceFolder}/src"
      ],
      "env": {},
      "disabled": false,
      "autoApprove": ["read_file", "list_directory"]
    },
    "git": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-git",
        "--repository",
        "${workspaceFolder}"
      ],
      "env": {},
      "disabled": false,
      "autoApprove": ["git_status", "git_log"]
    },
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ],
      "env": {},
      "disabled": false,
      "autoApprove": ["create_entities", "search_entities"]
    }
  }
}
```

This configuration includes only the essential servers for the AI Test Automation Platform.
