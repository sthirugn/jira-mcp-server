# Weekly Team Summary Generator

A comprehensive tool for generating weekly Jira team summaries organized by functional areas.

## 📋 Overview

This tool fetches Jira tickets from your team's filter and categorizes them into four key areas:

1. **Remediations Core** - Core remediation functionality and frontend work
2. **Remediations Platform** - Platform services (Playbook Dispatcher, Cloud Connector) and metrics work  
3. **QE / Integrations** - Quality engineering, integration testing (Eventing, Policies, Floorist, IQE projects)
4. **Edge Decommission** - HMS project and edge decommission work

## 🚀 Quick Start

### Method 1: Using the Wrapper Script (Recommended)

```bash
# Current week summary
./run_weekly_summary.sh current

# Last week summary  
./run_weekly_summary.sh last

# Specific week (starting from date)
./run_weekly_summary.sh 2024-07-15

# Custom date range
./run_weekly_summary.sh 2024-07-15 2024-07-22

# Show help
./run_weekly_summary.sh help
```

### Method 2: Direct Python Script

```bash
# Current week (automatically calculated)
python3 weekly_team_summary.py

# Specific date range
python3 weekly_team_summary.py 2024-07-15 2024-07-22

# Week starting from specific date
python3 weekly_team_summary.py 2024-07-15
```

## 📊 Sample Output

The tool generates both console output and saves a detailed report file:

```
================================================================================
📊 WEEKLY TEAM SUMMARY: 2024-07-15 to 2024-07-22
================================================================================
Generated: 2024-07-22 22:36:13

📈 OVERVIEW:
   Total Tickets: 36
   Remediations Core: 23 tickets
   QE / Integrations: 5 tickets
   Other: 8 tickets

============================================================
🎯 REMEDIATIONS CORE
📝 Core remediation functionality and frontend work
============================================================

📌 Closed (23 tickets):
   • RHINENG-8445: CVE-2024-21501 sanitize-html: Information Exposure...
     Assignee: Samuel Oleksak | Priority: Normal
     Components: Advisor, Frontend, Tasks
     Updated: 2024-07-18 | URL: https://issues.redhat.com/browse/RHINENG-8445
   
   [... more tickets ...]
```

## ⚙️ Configuration

### Prerequisites

1. **Virtual Environment**: Activate your Python virtual environment with required packages:
   ```bash
   source .mcp_venv/bin/activate  # or wherever your venv is
   ```

2. **Jira Credentials**: Ensure your `.env` file is configured:
   ```bash
   JIRA_SERVER=https://issues.redhat.com/
   JIRA_EMAIL=your-email@redhat.com
   JIRA_API_TOKEN=your-api-token
   ```

3. **Dependencies**: Install required packages:
   ```bash
   pip install mcp jira python-dotenv PyYAML
   ```

### Team Configuration

The tool now uses external YAML configuration files for maximum flexibility:

1. **Copy the template**:
   ```bash
   cp team_config_example.yaml my_team_config.yaml
   ```

2. **Edit for your team**:
   - Update `base_jql` with your projects, components, and team members
   - Customize `team_categories` for your organization structure
   - Configure `status_filters` and `report_settings`

3. **Use your configuration**:
   ```bash
   python3 weekly_team_summary.py 2025-07-15 2025-07-22 my_team_config.yaml
   ```

For detailed configuration instructions, see **[CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)**.

### Team Filter Configuration

The tool uses a comprehensive JQL filter that includes:

- **Project-based filtering**: RHINENG, IQE, HMS, Insights Experiences
- **Component-based filtering**: Drift, Eventing, Policies, Remediations, Playbook Dispatcher, Cloud Connector, Floorist
- **Team member assignments**: Assignee, Contributors, QA Contact fields
- **Date range filtering**: Updated within the specified week

## 🎯 Categorization Rules

### Remediations Core
- **Components**: Remediations, Frontend
- **Focus**: Core remediation functionality and UI work

### Remediations Platform  
- **Components**: Playbook Dispatcher, Cloud Connector
- **Keywords**: metrics, metric
- **Focus**: Platform services and observability

### QE / Integrations
- **Components**: Eventing, Policies, Floorist
- **Projects**: IQE
- **Focus**: Quality engineering and integration testing

### Edge Decommission
- **Projects**: HMS
- **Keywords**: hms, edge, decommission
- **Focus**: Edge infrastructure migration work

## 📁 Output Files

Reports are automatically saved in the `Reports/` directory as `team_summary_YYYY-MM-DD_to_YYYY-MM-DD.txt` with:

- Executive summary with ticket counts by category
- Detailed sections for each team area
- Tickets grouped by status (Closed, In Progress, etc.)
- Full ticket details: assignee, priority, components, URLs
- Uncategorized tickets section

## 🔧 Customization

### Modifying Team Categories

Edit `weekly_team_summary.py` and update the `team_categories` dictionary:

```python
self.team_categories = {
    'Your Team Name': {
        'components': ['Component1', 'Component2'],
        'projects': ['PROJECT_KEY'],
        'keywords': ['keyword1', 'keyword2'],
        'description': 'Team description'
    }
}
```

### Adjusting the JQL Filter

Modify the `base_jql` in the `WeeklyTeamSummary` class to include different projects, components, or team members.

### Custom Date Ranges

The tool supports flexible date handling:
- No arguments: Current week (Monday-Sunday)
- One date: Week starting from that date  
- Two dates: Custom date range
- Special keywords: "current", "last", "this"

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated and dependencies installed
2. **Jira Connection**: Verify `.env` credentials and VPN access if required
3. **No Tickets Found**: Check date range and JQL filter scope
4. **Permission Issues**: Ensure your Jira account has access to relevant projects

### Debug Mode

For detailed error information, run with Python directly:
```bash
python3 weekly_team_summary.py 2024-07-15 2024-07-22
```

### Jira Connection Test

Test your Jira connectivity:
```bash
python3 test_connection.py
```

## 📈 Usage Patterns

### Weekly Standup Reports
```bash
# Generate last week's summary for Monday standup
./run_weekly_summary.sh last
```

### Sprint Planning
```bash
# Review current week progress
./run_weekly_summary.sh current
```

### Monthly Reviews
```bash
# Generate multiple weekly reports
./run_weekly_summary.sh 2024-07-01 2024-07-07
./run_weekly_summary.sh 2024-07-08 2024-07-14
./run_weekly_summary.sh 2024-07-15 2024-07-21
./run_weekly_summary.sh 2024-07-22 2024-07-28
```

## 🤝 Contributing

To extend this tool:

1. **Add new team categories**: Update `team_categories` dictionary
2. **Modify output format**: Edit `generate_summary_report()` method
3. **Add new filters**: Extend the `base_jql` or categorization logic
4. **Custom integrations**: Use the `WeeklyTeamSummary` class in your own scripts

---

**Need help?** Check the Jira MCP server documentation or run `./run_weekly_summary.sh help` for quick reference. 