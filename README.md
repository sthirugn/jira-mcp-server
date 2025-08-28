# Jira MCP Server

A clean and focused Model Context Protocol (MCP) server that provides seamless integration between AI assistants and Jira, enabling natural language interaction with your Jira projects, issues, and workflows.

## 🎯 Features

- **11 Comprehensive Tools** for full Jira interaction
- **Natural Language Interface** - Ask AI to manage your Jira work
- **Real-time Updates** - Get current project status and issue information
- **Secure Authentication** - API token-based authentication
- **Cross-platform** - Works with any MCP-compatible client
- **Easy Setup** - Simple configuration and testing

## 🛠️ Available Tools

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `get_issue` | Get detailed issue info | `get_issue(issue_key="PROJ-12345")` |
| `search_issues` | Search with JQL | `search_issues(jql="project = PROJ")` |
| `create_issue` | Create new issue | `create_issue(project_key="PROJ", issue_type="Bug", summary="...")` |
| `update_issue` | Update existing issue | `update_issue(issue_key="PROJ-12345", summary="New title")` |
| `add_comment` | Add comment to issue | `add_comment(issue_key="PROJ-12345", comment="...")` |
| `get_comments` | Get all comments | `get_comments(issue_key="PROJ-12345")` |
| `transition_issue` | Move through workflow | `transition_issue(issue_key="PROJ-12345", transition_name="In Progress")` |
| `get_project` | Get project info | `get_project(project_key="PROJ")` |
| `get_issue_types` | Get available types | `get_issue_types(project_key="PROJ")` |
| `get_my_issues` | Get assigned issues | `get_my_issues(max_results=20)` |
| `get_project_issues` | Get project issues | `get_project_issues(project_key="PROJ")` |

## 🚀 Quick Start (5 minutes)

### Prerequisites

- Python 3.8 or higher
- Jira account with API access
- MCP-compatible client (Cursor, VS Code, etc.)

### 1. Clone and Setup

```bash
cd jira-mcp-server
pip install -r requirements.txt
```

### 2. Configure Credentials

Create a `.env` file with your Jira details:

```bash
JIRA_SERVER=https://your-company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-api-token
```

**Getting Your API Token:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the token to your `.env` file

### 3. Test Connection

```bash
python3 test_connection.py
```



### 4. Configure MCP Client

#### For Cursor:
Add to `~/.cursor/mcp_servers.json`:

```json
{
  "mcpServers": {
    "jira": {
      "command": "python3",
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

#### For VS Code:
Add to your VS Code MCP configuration:

```json
{
  "mcpServers": {
    "jira": {
      "command": "python3",
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

### 5. Start the Server

```bash
python3 server.py
```

### 6. Restart and Test

Restart your MCP client and try these commands:

- "Show me all open issues in project XYZ"
- "Create a new task for fixing the login bug"
- "Search for high priority bugs assigned to me"

## 📁 Project Structure

```
jira-mcp-server/
├── server.py              # Main MCP server implementation
├── test_connection.py     # Connection test script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
└── README.md              # This file
```

## 🔗 Related Projects

- **[Jira Weekly Reports](https://github.com/sthirugn/jira-weekly-reports)** - Generate automated weekly team summaries from Jira tickets

## 🎯 Usage Examples

### Get Your Issues
```python
# Get issues assigned to you
get_my_issues(max_results=10)
```

### Search for Specific Issues
```python
# Find high priority bugs
search_issues(jql="project = PROJ AND priority = High AND type = Bug")

# Find recent updates
search_issues(jql="project = PROJ AND updated >= -7d")
```

### Create New Issue
```python
create_issue(
    project_key="PROJ",
    issue_type="Task",
    summary="Implement new feature",
    description="Add support for advanced filtering",
    priority="Medium"
)
```

### Update Issue Status
```python
transition_issue(
    issue_key="PROJ-12345",
    transition_name="In Progress"
)
```

### Get Issue Details
```python
# Get details for issue PROJ-12345
get_issue(issue_key="PROJ-12345")
```

### Search Issues
```python
# Search for open issues in PROJ project
search_issues(jql="project = PROJ AND status = Open", max_results=10)
```

## 🔍 JQL Query Examples

### Common Patterns
```jql
# Your assigned issues
assignee = currentUser()

# Issues in specific project
project = PROJ

# Open issues
status = Open

# Issues updated in last 7 days
updated >= -7d

# High priority issues
priority = High

# Issues with specific component
component = "Backend"

# Status filters
status IN ("In Progress", "Code Review")

# Date filters
created >= "2025-01-01"

# Priority filters
priority IN ("High", "Critical")

# Combined queries
project = PROJ AND status = Open AND priority = High
assignee = currentUser() AND updated >= -3d
```

## 🧪 Testing Your Setup

### 1. Connection Test
```bash
python3 test_connection.py
```
✅ Should show: "Successfully connected to Jira"

### 2. Start Server (Optional Test)
```bash
python3 server.py
```
✅ Should start the MCP server and wait for connections.

### 3. Individual Tool Test
```bash
# Test search functionality
python3 -c "
import asyncio
from server import JiraMCPServer

async def test():
    server = JiraMCPServer()
    await server._init_jira_client()
    result = await server._search_issues('project = PROJ', max_results=3)
    print(f'Found {len(result)} results')

asyncio.run(test())
"
```

## 🚀 Starting the Server

Simply run the server directly:

```bash
python3 server.py
```

**Note:** Make sure you've completed the setup steps above (installing dependencies, creating `.env` file, and testing connection) before starting the server.

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use API tokens** instead of passwords
3. **Rotate tokens regularly**
4. **Limit token permissions** to minimum required
5. **Use environment variables** for sensitive data

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Error**
   - Check your API token is correct
   - Ensure your email matches your Jira account
   - Verify token hasn't expired

2. **Connection Error**
   - Check your internet connection
   - Verify JIRA_SERVER URL is correct
   - Ensure firewall allows HTTPS connections

3. **Permission Error**
   - Check your Jira permissions
   - Verify you have access to the project/issue
   - Contact your Jira administrator

4. **"Permission denied" errors**
   - Run: `chmod +x server.py test_connection.py`

5. **"Module not found" errors**
   - Run: `pip install -r requirements.txt`

6. **Cursor doesn't see the server**
   - Double-check the absolute path in your MCP config
   - Restart Cursor completely
   - Check that the `.env` file has the correct credentials

### Debug Mode

Enable debug logging by modifying the logging level in `server.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 🛠️ Development

### Adding New Tools

1. Add tool definition to `list_tools()` method
2. Add handler in `call_tool()` method
3. Implement the actual tool method
4. Update this README

### Error Handling

The server includes comprehensive error handling:
- Connection errors
- Authentication failures
- Invalid issue keys
- JQL syntax errors
- Permission errors

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🎉 Success!

Your Jira MCP server is now properly configured and ready to use! You can:

- ✅ Search and view Jira issues
- ✅ Create and update issues
- ✅ Manage comments and transitions
- ✅ Get project information
- ✅ Handle your assigned work

The server provides a powerful interface between AI assistants and your Jira workflow, making it easier to manage projects and track progress.

## 📈 What's Next?

Once it's working, you can:
- Ask about specific issues: "What's the status of PROJ-123?"
- Create issues: "Create a bug report for the navbar not working"
- Search with JQL: "Find all issues in project ABC that are in review"
- Add comments: "Add a comment to PROJ-456 saying testing is complete"
- Transition issues: "Move PROJ-789 to Done"

Enjoy your new Jira integration! 🎉 