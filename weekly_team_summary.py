#!/usr/bin/env python3
"""
Weekly Team Summary Generator for Jira Tickets

Generates weekly summaries of team work based on Jira tickets, categorized by team areas:
1. Remediations Core
2. Remediations Platform  
3. QE / Integrations
4. Edge Decommission

Usage:
    python3 weekly_team_summary.py [start_date] [end_date] [config_file]
    
Examples:
    python3 weekly_team_summary.py 2025-07-15 2025-07-22
    python3 weekly_team_summary.py  # Uses current week
    python3 weekly_team_summary.py 2025-07-15 2025-07-22 custom_team_config.yaml
"""

import asyncio
import sys
import os
import yaml
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict

# Add current directory to path for imports
sys.path.insert(0, '.')

from dotenv import load_dotenv
from server import JiraMCPServer

# Load environment variables
load_dotenv()

class WeeklyTeamSummary:
    def __init__(self, config_file='team_config.yaml'):
        self.server = None
        self.config = self._load_config(config_file)
        self.base_jql = self.config['base_jql']
        self.team_categories = self.config['team_categories']
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            print(f"✅ Loaded configuration from {config_file}")
            return config
        except FileNotFoundError:
            print(f"❌ Configuration file {config_file} not found!")
            print("Please create a team_config.yaml file or specify a valid config file.")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML configuration: {e}")
            sys.exit(1)
            

        
    async def initialize(self):
        """Initialize the Jira MCP server connection"""
        self.server = JiraMCPServer()
        await self.server._init_jira_client()
        print("✅ Connected to Jira")
        
    def build_jql_with_dates(self, start_date: str, end_date: str) -> str:
        """Build JQL query with date range filter"""
        date_filter = f'updated >= "{start_date}" AND updated <= "{end_date}"'
        
        # Add status filter if configured
        filters = [f'({self.base_jql})', f'({date_filter})']
        
        if 'status_filters' in self.config and 'exclude' in self.config['status_filters']:
            excluded_statuses = self.config['status_filters']['exclude']
            if excluded_statuses:
                status_list = ', '.join([f'"{status}"' for status in excluded_statuses])
                status_filter = f'status NOT IN ({status_list})'
                filters.append(f'({status_filter})')
        
        # Get order by from config
        order_by = self.config.get('report_settings', {}).get('order_by', 'component ASC, updated DESC')
        
        return ' AND '.join(filters) + f' ORDER BY {order_by}'
        
    async def fetch_tickets(self, start_date: str, end_date: str) -> List[Any]:
        """Fetch tickets for the specified date range"""
        jql = self.build_jql_with_dates(start_date, end_date)
        print(f"🔍 Searching tickets from {start_date} to {end_date}...")
        
        try:
            # Get max results from config
            max_results = self.config.get('report_settings', {}).get('max_results', 200)
            issues = self.server.jira_client.search_issues(jql, maxResults=max_results)
            print(f"📊 Found {len(issues)} tickets")
            return issues
        except Exception as e:
            print(f"❌ Error fetching tickets: {e}")
            return []
            
    def categorize_ticket(self, issue) -> str:
        """Categorize a ticket into one of the team categories"""
        # Get ticket details
        components = [comp.name for comp in getattr(issue.fields, 'components', [])]
        project = issue.fields.project.key
        summary = issue.fields.summary.lower()
        description = (issue.fields.description or "").lower()
        
        # Check each category
        for category_name, rules in self.team_categories.items():
            # Check components
            if 'components' in rules:
                if any(comp in components for comp in rules['components']):
                    return category_name
                    
            # Check projects
            if 'projects' in rules:
                if project in rules['projects']:
                    return category_name
                    
            # Check keywords in summary/description
            if 'keywords' in rules:
                text_to_search = f"{summary} {description}"
                if any(keyword in text_to_search for keyword in rules['keywords']):
                    return category_name
                    
        # Default category for uncategorized tickets
        return 'Other'
        
    def format_ticket_info(self, issue) -> Dict[str, str]:
        """Format ticket information for display"""
        return {
            'key': issue.key,
            'summary': issue.fields.summary,
            'status': issue.fields.status.name,
            'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
            'priority': issue.fields.priority.name if issue.fields.priority else 'None',
            'components': [comp.name for comp in getattr(issue.fields, 'components', [])],
            'updated': str(issue.fields.updated)[:10],  # Just the date part
            'url': f"{self.server.jira_client.server_url}/browse/{issue.key}"
        }
    
    def format_table_row(self, ticket_info: Dict[str, str], title_width=50, assignee_width=20) -> str:
        """Format a single ticket as a table row"""
        # Create markdown link for ticket ID
        ticket_link = f"[{ticket_info['key']}]({ticket_info['url']})"
        
        # Truncate title if too long
        title = ticket_info['summary']
        if len(title) > title_width:
            title = title[:title_width-3] + "..."
        
        # Truncate assignee if too long  
        assignee = ticket_info['assignee']
        if len(assignee) > assignee_width:
            assignee = assignee[:assignee_width-3] + "..."
        
        return f"| {ticket_link:<25} | {assignee:<{assignee_width}} | {ticket_info['priority']:<8} | {ticket_info['updated']:<10} | {title:<{title_width}} |"
        
    def generate_summary_report(self, categorized_tickets: Dict[str, List], start_date: str, end_date: str) -> str:
        """Generate a formatted summary report"""
        report = []
        report.append(f"## 📊 WEEKLY TEAM SUMMARY: {start_date} to {end_date}")
        report.append("")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary statistics
        total_tickets = sum(len(tickets) for tickets in categorized_tickets.values())
        report.append(f"### 📈 OVERVIEW")
        report.append(f"- **Total Tickets:** {total_tickets}")
        for category, tickets in categorized_tickets.items():
            if tickets:  # Only show categories with tickets
                report.append(f"- **{category}:** {len(tickets)} tickets")
        report.append("")
        
        # Detailed sections
        for category_name, category_rules in self.team_categories.items():
            tickets = categorized_tickets.get(category_name, [])
            
            report.append(f"### 🎯 {category_name.upper()} - {category_rules['description']}")
            report.append("")
            
            if not tickets:
                report.append("*No tickets found for this category this week.*")
                report.append("")
                continue
                
            # Group by status
            status_groups = defaultdict(list)
            for ticket in tickets:
                ticket_info = self.format_ticket_info(ticket)
                status_groups[ticket_info['status']].append(ticket_info)
                
            for status, status_tickets in status_groups.items():
                report.append(f"#### 📌 {status} ({len(status_tickets)} tickets)")
                report.append("")
                
                # Add table header
                report.append("| Ticket ID                | Assignee             | Priority | Updated    | Title                                              |")
                report.append("|--------------------------|----------------------|----------|------------|----------------------------------------------------| ")
                
                # Add ticket rows
                for ticket in status_tickets:
                    report.append(self.format_table_row(ticket))
                report.append("")
                    
        # Handle uncategorized tickets
        other_tickets = categorized_tickets.get('Other', [])
        if other_tickets:
            report.append("### 🔍 OTHER / UNCATEGORIZED TICKETS")
            report.append("")
            
            # Add table header
            report.append("| Ticket ID                | Assignee             | Priority | Updated    | Title                                              |")
            report.append("|--------------------------|----------------------|----------|------------|----------------------------------------------------| ")
            
            # Add ticket rows
            for ticket in other_tickets:
                ticket_info = self.format_ticket_info(ticket)
                report.append(self.format_table_row(ticket_info))
            report.append("")
                
        report.append("---")
        report.append("")
        report.append("### ✅ Report Complete")
        report.append("")
        report.append("*This report was generated automatically from Jira data.*")
        
        return "\n".join(report)
        
    async def generate_weekly_summary(self, start_date: str, end_date: str) -> str:
        """Generate the complete weekly summary"""
        await self.initialize()
        
        # Fetch tickets
        tickets = await self.fetch_tickets(start_date, end_date)
        
        if not tickets:
            return f"No tickets found for the period {start_date} to {end_date}"
            
        # Categorize tickets
        categorized_tickets = defaultdict(list)
        for ticket in tickets:
            category = self.categorize_ticket(ticket)
            categorized_tickets[category].append(ticket)
            
        # Generate report
        return self.generate_summary_report(categorized_tickets, start_date, end_date)
        
def parse_date_args():
    """Parse command line date arguments or use current week"""
    if len(sys.argv) >= 3:
        start_date = sys.argv[1]
        end_date = sys.argv[2]
    elif len(sys.argv) == 2:
        # Single date provided, assume it's the start of the week
        start_date = sys.argv[1]
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = start_dt + timedelta(days=6)
        end_date = end_dt.strftime('%Y-%m-%d')
    else:
        # No dates provided, use current week (Monday to Sunday)
        today = datetime.now()
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        sunday = monday + timedelta(days=6)
        start_date = monday.strftime('%Y-%m-%d')
        end_date = sunday.strftime('%Y-%m-%d')
        
    return start_date, end_date

async def main():
    """Main function"""
    try:
        start_date, end_date = parse_date_args()
        
        print(f"🚀 Generating weekly team summary for {start_date} to {end_date}")
        print("=" * 60)
        
        # Check for custom config file argument
        config_file = 'team_config.yaml'
        if len(sys.argv) >= 4 and sys.argv[3].endswith('.yaml'):
            config_file = sys.argv[3]
            print(f"📝 Using custom config file: {config_file}")
        
        summary_generator = WeeklyTeamSummary(config_file)
        report = await summary_generator.generate_weekly_summary(start_date, end_date)
        
        # Create Reports directory if it doesn't exist
        reports_dir = "Reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Save report to file in Reports directory (as Markdown for better formatting)
        filename = f"team_summary_{start_date}_to_{end_date}.md"
        filepath = os.path.join(reports_dir, filename)
        with open(filepath, 'w') as f:
            f.write(report)
            
        print(f"📄 Report saved to: {filepath}")
        print("\n" + report)
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 