# Jira MCP Server - Quick Start Guide

Get your Jira MCP server up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Jira account with API access
- Cursor editor

## Step 1: Setup

```bash
cd jira-mcp-server
python setup.py
```

This will:
- Install required Python packages
- Create a `.env` file from the template
- Make scripts executable

## Step 2: Configure Credentials

Edit the `.env` file with your Jira details:

```env
JIRA_SERVER=https://your-company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-api-token
```

### Getting Your API Token:
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the token to your `.env` file

## Step 3: Test Connection

```bash
python test_connection.py
```

This verifies your credentials and connection work.

## Step 4: Add to Cursor

Add this to your Cursor MCP settings file:

**Location:** `~/.cursor/mcp_servers.json` (create if it doesn't exist)

```json
{
  "mcpServers": {
    "jira": {
      "command": "python",
      "args": ["/full/path/to/jira-mcp-server/server.py"],
      "env": {
        "JIRA_SERVER": "https://your-company.atlassian.net",
        "JIRA_EMAIL": "your-email@company.com",
        "JIRA_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

**Important:** Use the full absolute path to `server.py`!

## Step 5: Restart Cursor

Restart Cursor to load the new MCP server.

## Step 6: Test in Cursor

Try these commands in Cursor chat:

- "Show me all open issues in project XYZ"
- "Create a new task for fixing the login bug"
- "Search for high priority bugs assigned to me"

## Common Issues

### "Permission denied" errors
- Run: `chmod +x server.py setup.py test_connection.py`

### "Module not found" errors
- Run: `pip install -r requirements.txt`

### "Authentication failed" errors
- Verify your API token hasn't expired
- Check your email address is correct
- Ensure the server URL includes `https://`

### Cursor doesn't see the server
- Double-check the absolute path in your MCP config
- Restart Cursor completely
- Check that the `.env` file has the correct credentials

## Need Help?

1. Run `python test_connection.py` to debug connection issues
2. Check the full README.md for detailed documentation
3. Verify your Jira permissions allow the operations you're trying

## What's Next?

Once it's working, you can:
- Ask about specific issues: "What's the status of PROJ-123?"
- Create issues: "Create a bug report for the navbar not working"
- Search with JQL: "Find all issues in project ABC that are in review"
- Add comments: "Add a comment to PROJ-456 saying testing is complete"
- Transition issues: "Move PROJ-789 to Done"

Enjoy your new Jira integration! 🎉 