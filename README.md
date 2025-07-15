# Jira MCP Server

A Model Context Protocol (MCP) server that provides seamless integration with Jira from Cursor and other MCP-compatible tools.

## Features

- **Issue Management**: Create, read, update, and search Jira issues
- **Project Information**: Get project details and configurations
- **Comments**: Add and retrieve comments on issues
- **Transitions**: Move issues through workflows
- **Search**: Advanced JQL-based issue searching
- **Attachments**: Handle file attachments (read-only)

## Installation

1. Clone or create the MCP server directory:
```bash
mkdir jira-mcp-server
cd jira-mcp-server
```

2. Install dependencies:
```bash
pip install mcp jira python-dotenv
```

3. Create a `.env` file with your Jira configuration:
```env
JIRA_SERVER=https://your-company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-api-token
```

### Getting Jira API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a label (e.g., "MCP Server")
4. Copy the generated token to your `.env` file

## Configuration in Cursor

Add this to your Cursor MCP settings (usually in `~/.cursor/mcp_servers.json`):

```json
{
  "mcpServers": {
    "jira": {
      "command": "python",
      "args": ["/path/to/jira-mcp-server/server.py"],
      "env": {
        "JIRA_SERVER": "https://your-company.atlassian.net",
        "JIRA_EMAIL": "your-email@company.com",
        "JIRA_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

## Available Tools

### `get_issue`
Get detailed information about a specific Jira issue.
- **Parameters**: `issue_key` (e.g., "PROJ-123")

### `search_issues`
Search for issues using JQL (Jira Query Language).
- **Parameters**: `jql` (e.g., "project = PROJ AND status = Open")
- **Optional**: `max_results` (default: 50)

### `create_issue`
Create a new Jira issue.
- **Parameters**: 
  - `project_key`: Project key (e.g., "PROJ")
  - `issue_type`: Issue type (e.g., "Task", "Bug", "Story")
  - `summary`: Issue title
  - `description`: Issue description
  - `priority`: Priority level (optional)

### `update_issue`
Update an existing issue.
- **Parameters**:
  - `issue_key`: Issue key
  - `summary`: New summary (optional)
  - `description`: New description (optional)

### `add_comment`
Add a comment to an issue.
- **Parameters**:
  - `issue_key`: Issue key
  - `comment`: Comment text

### `get_comments`
Get all comments for an issue.
- **Parameters**: `issue_key`

### `transition_issue`
Move an issue through workflow states.
- **Parameters**:
  - `issue_key`: Issue key
  - `transition_name`: Name of transition (e.g., "In Progress", "Done")

### `get_project`
Get information about a project.
- **Parameters**: `project_key`

### `get_issue_types`
Get available issue types for a project.
- **Parameters**: `project_key`

## Usage Examples

### In Cursor Chat:
- "Show me all open bugs in project ABC"
- "Create a new task for implementing user authentication"
- "Add a comment to issue ABC-123 about the testing status"
- "Move issue ABC-456 to In Progress"
- "Search for issues assigned to me that are high priority"

## Troubleshooting

### Authentication Issues
- Verify your API token is correct and hasn't expired
- Ensure your email matches your Atlassian account
- Check that your Jira server URL is correct (include https://)

### Permission Issues
- Ensure your account has appropriate permissions for the operations you're trying to perform
- Some operations may require project admin or specific role permissions

### Connection Issues
- Verify your Jira server is accessible
- Check if your organization has IP restrictions or VPN requirements
- Ensure the Jira server URL doesn't have trailing slashes

## Security Notes

- Store API tokens securely and never commit them to version control
- Consider using environment variables or secure credential storage
- Regularly rotate your API tokens
- Use the principle of least privilege for your Jira account

## Contributing

Feel free to extend this MCP server with additional Jira functionality such as:
- Sprint management
- Board operations
- Advanced field handling
- Bulk operations
- Custom field support 