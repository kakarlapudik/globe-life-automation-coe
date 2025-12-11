# MCP (Model Context Protocol) Integration Guide

## Overview

This guide covers the integration of MCP servers from the official repository (https://github.com/modelcontextprotocol/servers) into the AI Test Automation Platform.

## Current MCP Server Configuration

The platform is configured with the following MCP servers:

### 1. **Filesystem Server** (Active)
- **Purpose**: File system operations for code analysis and test generation
- **Capabilities**: Read files, list directories, search files
- **Use Cases**:
  - Code analysis for test generation
  - Test artifact management
  - File-based test data access

### 2. **Git Server** (Active)
- **Purpose**: Version control operations for change tracking
- **Capabilities**: Git status, diff, log, blame
- **Use Cases**:
  - Change impact analysis
  - Regression test identification
  - Code history analysis for test recommendations

### 3. **GitHub Server** (Active)
- **Purpose**: GitHub API integration
- **Capabilities**: Search repositories, get file contents, list commits
- **Use Cases**:
  - Pull request analysis
  - Repository insights
  - Collaborative test development

### 4. **SQLite Server** (Active)
- **Purpose**: Database operations for test analytics
- **Capabilities**: Query test results, analytics data
- **Use Cases**:
  - Test execution history
  - Performance metrics storage
  - Test data management

### 5. **Puppeteer Server** (Active)
- **Purpose**: Browser automation for UI testing
- **Capabilities**: Screenshots, navigation, element interaction
- **Use Cases**:
  - Visual regression testing
  - Dynamic test case discovery
  - UI element detection

### 6. **Memory Server** (Active)
- **Purpose**: Context and knowledge management
- **Capabilities**: Store and retrieve entities, semantic search
- **Use Cases**:
  - Test context persistence
  - Knowledge base for test patterns
  - Session management

### 7. **Fetch Server** (Active)
- **Purpose**: HTTP requests for API testing
- **Capabilities**: Make HTTP requests, handle responses
- **Use Cases**:
  - API endpoint testing
  - External service integration
  - Web scraping for test data

### 8. **PostgreSQL Server** (Disabled)
- **Purpose**: Advanced database operations
- **Capabilities**: Complex queries, transactions
- **Use Cases**:
  - Enterprise test data management
  - Large-scale analytics

### 9. **Brave Search Server** (Disabled)
- **Purpose**: Web search capabilities
- **Capabilities**: Search the web for information
- **Use Cases**:
  - Research test patterns
  - Find documentation
  - Discover best practices

### 10. **Slack Server** (Disabled)
- **Purpose**: Team collaboration and notifications
- **Capabilities**: Send messages, read channels
- **Use Cases**:
  - Test failure notifications
  - Team collaboration
  - Status updates

## Configuration

### Environment Variables Required

Create a `.env` file in your workspace root with the following variables:

```bash
# GitHub Integration
GITHUB_TOKEN=your_github_personal_access_token

# Brave Search (if enabled)
BRAVE_API_KEY=your_brave_api_key

# Slack Integration (if enabled)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_TEAM_ID=your-slack-team-id
```

### Enabling/Disabling Servers

To enable or disable a server, modify the `disabled` field in `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "server-name": {
      "disabled": false  // Set to true to disable
    }
  }
}
```

## Integration with Platform Features

### Test Generation Agent
- **Uses**: Filesystem, Git, GitHub, Memory
- **Purpose**: Analyze code changes and generate appropriate tests

### Pattern Detection Agent
- **Uses**: SQLite, Memory, Git
- **Purpose**: Identify test patterns and anti-patterns from history

### Diagnostic Agent
- **Uses**: Git, GitHub, SQLite
- **Purpose**: Root cause analysis using code history and test data

### Remediation Agent
- **Uses**: Filesystem, Git, Memory
- **Purpose**: Auto-fix test failures based on patterns

### Visual Testing
- **Uses**: Puppeteer, Filesystem, Memory
- **Purpose**: Capture and compare UI screenshots

## Troubleshooting

### "Unexpected end of JSON input" Error

This error typically occurs when:

1. **Empty or corrupted file**: The mcp.json file is empty or truncated
   - **Solution**: Restore from backup or recreate the file

2. **Trailing comma**: JSON doesn't allow trailing commas
   - **Solution**: Remove any trailing commas in the JSON

3. **File encoding issues**: The file has incorrect encoding
   - **Solution**: Save the file as UTF-8

4. **File permissions**: The file cannot be read
   - **Solution**: Check file permissions

### Server Connection Issues

If a server fails to connect:

1. **Check Node.js**: Ensure Node.js and npx are installed
   ```bash
   node --version
   npx --version
   ```

2. **Check environment variables**: Verify all required env vars are set
   ```bash
   echo $GITHUB_TOKEN
   ```

3. **Test server manually**: Run the server command directly
   ```bash
   npx -y @modelcontextprotocol/server-filesystem ./src
   ```

4. **Check logs**: Look for error messages in the MCP server logs

### Auto-Approval Configuration

To automatically approve certain MCP tool calls, add them to the `autoApprove` array:

```json
{
  "autoApprove": [
    "read_file",
    "list_directory",
    "search_files"
  ]
}
```

## Best Practices

1. **Start with essential servers**: Enable only the servers you need
2. **Use auto-approve carefully**: Only auto-approve safe, read-only operations
3. **Monitor server usage**: Track which servers are being used most
4. **Keep credentials secure**: Never commit API keys to version control
5. **Test server connectivity**: Verify servers are working before relying on them

## Adding New MCP Servers

To add a new MCP server from the official repository:

1. Find the server in https://github.com/modelcontextprotocol/servers
2. Add configuration to `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "new-server": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-name"],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

3. Restart Kiro or reconnect the MCP server
4. Test the server functionality

## Available Official MCP Servers

From https://github.com/modelcontextprotocol/servers:

- **@modelcontextprotocol/server-filesystem**: File system operations
- **@modelcontextprotocol/server-git**: Git operations
- **@modelcontextprotocol/server-github**: GitHub API
- **@modelcontextprotocol/server-gitlab**: GitLab API
- **@modelcontextprotocol/server-google-drive**: Google Drive integration
- **@modelcontextprotocol/server-google-maps**: Google Maps API
- **@modelcontextprotocol/server-memory**: Knowledge graph storage
- **@modelcontextprotocol/server-postgres**: PostgreSQL database
- **@modelcontextprotocol/server-puppeteer**: Browser automation
- **@modelcontextprotocol/server-slack**: Slack integration
- **@modelcontextprotocol/server-sqlite**: SQLite database
- **@modelcontextprotocol/server-brave-search**: Web search
- **@modelcontextprotocol/server-fetch**: HTTP requests
- **@modelcontextprotocol/server-aws-kb-retrieval**: AWS Knowledge Base
- **@modelcontextprotocol/server-sequential-thinking**: Reasoning support

## Support

For issues with MCP integration:
1. Check the official MCP documentation: https://modelcontextprotocol.io
2. Review server-specific docs: https://github.com/modelcontextprotocol/servers
3. Check Kiro MCP documentation in the command palette
