# Configuration Guide for Weekly Team Summary Tool

This guide explains how to configure the Weekly Team Summary tool for your own team and Jira environment.

## 📋 Overview

The tool has been refactored to use external configuration files, making it easy for different managers to customize:
- **JQL filters** for your team's projects and members
- **Team categorization rules** for organizing tickets
- **Status filters** to exclude certain ticket states
- **Report settings** like max results and sorting

## 🚀 Quick Setup

### 1. Copy Configuration Template
```bash
cp team_config_example.yaml my_team_config.yaml
```

### 2. Edit Your Configuration
```bash
# Edit the config file for your team
nano my_team_config.yaml
```

### 3. Run with Your Config
```bash
python3 weekly_team_summary.py 2025-07-15 2025-07-22 my_team_config.yaml
```

## ⚙️ Configuration File Structure

### Base JQL Filter
This is the core filter that defines which tickets belong to your team:

```yaml
base_jql: |
  (
      project = MYPROJECT AND Component in ("Backend", "Frontend", "API")
  ) OR (
      project in (MYPROJECT, TESTS) AND assignee in ("manager@company.com", "dev1@company.com")
  )
```

**Common patterns:**
- **By project + component**: `project = MYPROJECT AND Component in ("Backend", "Frontend")`
- **By assignee**: `assignee in ("user1@company.com", "user2@company.com")`
- **By contributor**: `Contributors in ("user1@company.com", "user2@company.com")`
- **By QA contact**: `"QA Contact" in ("qa1@company.com", "qa2@company.com")`
- **Multiple projects**: `project in (PROJECT1, PROJECT2, PROJECT3)`

### Team Categories
Define how tickets are grouped in your report:

```yaml
team_categories:
  Backend Development:
    components:           # Match by Jira component
      - "Backend"
      - "API"
    keywords:            # Match by keywords in summary/description
      - "database"
      - "service"
    projects:            # Match by project key
      - "BACKEND_PROJ"
    description: "Backend services and API development"
```

**Category matching rules:**
- **components**: Exact match with Jira component names
- **keywords**: Case-sensitive substring search in ticket summary/description
- **projects**: Exact match with Jira project keys
- **description**: Human-readable description for the report

### Status Filters
Exclude tickets in certain statuses:

```yaml
status_filters:
  exclude:
    - "New"           # Planning items
    - "Backlog"       # Future work
    - "Blocked"       # Stuck items
    - "Cancelled"     # Abandoned work
```

### Report Settings
Control report behavior:

```yaml
report_settings:
  max_results: 150                          # Max tickets to fetch
  order_by: "updated DESC"                  # Sort order for JQL
```

## 📝 Real-World Examples

### Example 1: Backend Team
```yaml
base_jql: |
  project = BACKEND AND (
    assignee in ("backend-lead@company.com", "dev1@company.com", "dev2@company.com") OR
    Component in ("API", "Database", "Services")
  )

team_categories:
  API Development:
    components: ["API"]
    keywords: ["endpoint", "rest", "graphql"]
    description: "API and service endpoints"
    
  Database Work:
    components: ["Database"]
    keywords: ["migration", "schema", "postgres"]
    description: "Database and data layer work"
    
  DevOps:
    keywords: ["deployment", "docker", "kubernetes"]
    description: "Infrastructure and deployment"
```

### Example 2: Multi-Project Team
```yaml
base_jql: |
  (project in (WEB, MOBILE, SHARED) AND assignee in ("team-lead@company.com")) OR
  (project = WEB AND Component in ("Frontend", "Backend")) OR
  (project = MOBILE AND Component in ("iOS", "Android"))

team_categories:
  Web Frontend:
    projects: ["WEB"]
    components: ["Frontend"]
    description: "Web application frontend"
    
  Mobile Development:
    projects: ["MOBILE"]
    components: ["iOS", "Android"]
    description: "Mobile applications"
    
  Shared Libraries:
    projects: ["SHARED"]
    description: "Shared components and libraries"
```

### Example 3: Security Team
```yaml
base_jql: |
  (
    project in (SECURITY, AUDIT) 
  ) OR (
    assignee in ("security-team@example.com") AND summary ~ "security-fix*"
  ) OR (
    labels in (security, vulnerability, compliance)
  )

team_categories:
  Vulnerability Management:
    keywords: ["security", "vulnerability", "fix"]
    description: "Security vulnerabilities and patches"
    
  Compliance:
    keywords: ["compliance", "audit", "certification"]
    description: "Compliance and audit work"
    
  Security Tools:
    keywords: ["scanner", "tool", "automation"]
    description: "Security tooling and automation"
```

## 🎯 Category Design Best Practices

### 1. **Specific to General**
Order categories from most specific to most general. The tool processes categories in order, so specific matches should come first.

### 2. **Mutually Exclusive**
Design categories to minimize overlap. A ticket will be assigned to the **first** matching category.

### 3. **Keywords Strategy**
- Use **lowercase** keywords for case-sensitive matching
- Include **common abbreviations** (e.g., "API", "UI", "DB")
- Add **technology names** (e.g., "kubernetes", "react", "postgres")

### 4. **Component Accuracy**
- Use **exact component names** from your Jira instance
- Check for **case sensitivity** (e.g., "Frontend" vs "frontend")
- Account for **spelling variations**

## 🔧 Testing Your Configuration

### 1. **Dry Run Test**
```bash
# Test with a small date range first
python3 weekly_team_summary.py 2025-07-22 2025-07-22 my_config.yaml
```

### 2. **Validate JQL**
Test your JQL filter directly in Jira:
1. Go to Jira → Issues → Search for Issues
2. Switch to Advanced (JQL) mode
3. Paste your `base_jql` content
4. Verify it returns expected tickets

### 3. **Check Categories**
Look at the "Other / Uncategorized" section in your report:
- If many tickets are uncategorized, refine your category rules
- Add missing components or keywords
- Consider creating broader catch-all categories

## 📊 Multiple Team Configurations

For organizations with multiple teams:

```bash
# Different config files for different teams
python3 weekly_team_summary.py 2025-07-15 2025-07-22 backend_team.yaml
python3 weekly_team_summary.py 2025-07-15 2025-07-22 frontend_team.yaml
python3 weekly_team_summary.py 2025-07-15 2025-07-22 devops_team.yaml
```

### Shared Base Configuration
Create a base configuration and extend it:

```yaml
# base_config.yaml
common_settings: &defaults
  status_filters:
    exclude: ["New", "Backlog", "Cancelled"]
  report_settings:
    max_results: 200
    order_by: "updated DESC"

# backend_team.yaml
<<: *defaults
base_jql: |
  project = BACKEND AND assignee in ("backend-team@company.com")
team_categories:
  # Backend-specific categories...
```

## 🐛 Troubleshooting

### Common Issues

1. **"No tickets found"**
   - Check your JQL syntax in Jira first
   - Verify project names and user emails
   - Ensure date range covers expected activity

2. **"Configuration file not found"**
   - Check file path and name spelling
   - Ensure file is in the same directory as the script
   - Use absolute paths if needed

3. **Many tickets in "Other"**
   - Add missing components to categories
   - Include additional keywords
   - Check component name case sensitivity

4. **YAML parsing errors**
   - Validate YAML syntax online
   - Check indentation (use spaces, not tabs)
   - Escape special characters in strings

### Debug Mode
Add debug information to your config:

```yaml
# Add to any category for debugging
team_categories:
  Debug Category:
    components: ["Debug"]
    keywords: ["debug"]
    description: "Debug - should catch specific tickets"
```

## 📈 Advanced Usage

### Custom Date Ranges
```bash
# Last week
python3 weekly_team_summary.py 2025-07-08 2025-07-14 my_config.yaml

# Current month
python3 weekly_team_summary.py 2025-07-01 2025-07-31 my_config.yaml

# Sprint cycles (2 weeks)
python3 weekly_team_summary.py 2025-07-01 2025-07-14 my_config.yaml
```

### Automation Scripts
Create wrapper scripts for regular reporting:

```bash
#!/bin/bash
# weekly_report.sh
DATE_START=$(date -d "last monday" +%Y-%m-%d)
DATE_END=$(date -d "last sunday" +%Y-%m-%d)

python3 weekly_team_summary.py $DATE_START $DATE_END backend_team.yaml
python3 weekly_team_summary.py $DATE_START $DATE_END frontend_team.yaml

# Reports are automatically saved in the Reports/ directory
echo "📄 Reports generated in: Reports/"
ls -lt Reports/ | head -5
```

## 📚 Additional Resources

- **Jira JQL Documentation**: [Atlassian JQL Guide](https://support.atlassian.com/jira-service-management/docs/use-advanced-search-with-jira-query-language-jql/)
- **YAML Syntax Guide**: [YAML.org](https://yaml.org/spec/1.2/spec.html)
- **Jira Component Management**: Configure components in your Jira project settings

---

**Need help?** The tool provides detailed error messages and suggestions for common configuration issues. 