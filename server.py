#!/usr/bin/env python3
"""
Jira MCP Server

A Model Context Protocol server that provides integration with Jira.
Allows AI assistants to interact with Jira issues, projects, and workflows.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Sequence

from dotenv import load_dotenv
from jira import JIRA
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
    ServerCapabilities,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JiraMCPServer:
    def __init__(self):
        self.server = Server("jira-mcp-server")
        self.jira_client: Optional[JIRA] = None
        self._setup_tools()
        
    def _setup_tools(self):
        """Set up all available tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available Jira tools"""
            return [
                Tool(
                    name="get_issue",
                    description="Get detailed information about a specific Jira issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The Jira issue key (e.g., PROJ-123)"
                            }
                        },
                        "required": ["issue_key"]
                    }
                ),
                Tool(
                    name="search_issues",
                    description="Search for Jira issues using JQL (Jira Query Language)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "jql": {
                                "type": "string",
                                "description": "JQL query string (e.g., 'project = PROJ AND status = Open')"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 50
                            }
                        },
                        "required": ["jql"]
                    }
                ),
                Tool(
                    name="create_issue",
                    description="Create a new Jira issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_key": {
                                "type": "string",
                                "description": "Project key (e.g., PROJ)"
                            },
                            "issue_type": {
                                "type": "string",
                                "description": "Issue type (e.g., Task, Bug, Story)"
                            },
                            "summary": {
                                "type": "string",
                                "description": "Issue title/summary"
                            },
                            "description": {
                                "type": "string",
                                "description": "Issue description"
                            },
                            "priority": {
                                "type": "string",
                                "description": "Priority level (e.g., High, Medium, Low)",
                                "default": "Medium"
                            }
                        },
                        "required": ["project_key", "issue_type", "summary", "description"]
                    }
                ),
                Tool(
                    name="update_issue",
                    description="Update an existing Jira issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The Jira issue key"
                            },
                            "summary": {
                                "type": "string",
                                "description": "New summary (optional)"
                            },
                            "description": {
                                "type": "string",
                                "description": "New description (optional)"
                            }
                        },
                        "required": ["issue_key"]
                    }
                ),
                Tool(
                    name="add_comment",
                    description="Add a comment to a Jira issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The Jira issue key"
                            },
                            "comment": {
                                "type": "string",
                                "description": "Comment text"
                            }
                        },
                        "required": ["issue_key", "comment"]
                    }
                ),
                Tool(
                    name="get_comments",
                    description="Get all comments for a Jira issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The Jira issue key"
                            }
                        },
                        "required": ["issue_key"]
                    }
                ),
                Tool(
                    name="transition_issue",
                    description="Move an issue through workflow states",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The Jira issue key"
                            },
                            "transition_name": {
                                "type": "string",
                                "description": "Name of the transition (e.g., 'In Progress', 'Done')"
                            }
                        },
                        "required": ["issue_key", "transition_name"]
                    }
                ),
                Tool(
                    name="get_project",
                    description="Get information about a Jira project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_key": {
                                "type": "string",
                                "description": "Project key"
                            }
                        },
                        "required": ["project_key"]
                    }
                ),
                Tool(
                    name="get_issue_types",
                    description="Get available issue types for a project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_key": {
                                "type": "string",
                                "description": "Project key"
                            }
                        },
                        "required": ["project_key"]
                    }
                ),
                Tool(
                    name="get_my_issues",
                    description="Get issues assigned to the current user",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 20
                            }
                        }
                    }
                ),
                Tool(
                    name="get_project_issues",
                    description="Get all issues for a specific project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_key": {
                                "type": "string",
                                "description": "Project key"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 50
                            }
                        },
                        "required": ["project_key"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            
            # Initialize Jira client if not already done
            if not self.jira_client:
                await self._init_jira_client()
            
            try:
                if name == "get_issue":
                    return await self._get_issue(arguments["issue_key"])
                elif name == "search_issues":
                    return await self._search_issues(
                        arguments["jql"],
                        arguments.get("max_results", 50)
                    )
                elif name == "create_issue":
                    return await self._create_issue(
                        arguments["project_key"],
                        arguments["issue_type"],
                        arguments["summary"],
                        arguments["description"],
                        arguments.get("priority", "Medium")
                    )
                elif name == "update_issue":
                    return await self._update_issue(
                        arguments["issue_key"],
                        arguments.get("summary"),
                        arguments.get("description")
                    )
                elif name == "add_comment":
                    return await self._add_comment(
                        arguments["issue_key"],
                        arguments["comment"]
                    )
                elif name == "get_comments":
                    return await self._get_comments(arguments["issue_key"])
                elif name == "transition_issue":
                    return await self._transition_issue(
                        arguments["issue_key"],
                        arguments["transition_name"]
                    )
                elif name == "get_project":
                    return await self._get_project(arguments["project_key"])
                elif name == "get_issue_types":
                    return await self._get_issue_types(arguments["project_key"])
                elif name == "get_my_issues":
                    return await self._get_my_issues(arguments.get("max_results", 20))
                elif name == "get_project_issues":
                    return await self._get_project_issues(
                        arguments["project_key"],
                        arguments.get("max_results", 50)
                    )
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
                    
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _init_jira_client(self):
        """Initialize the Jira client with credentials"""
        try:
            server = os.getenv("JIRA_SERVER")
            email = os.getenv("JIRA_EMAIL")
            api_token = os.getenv("JIRA_API_TOKEN")
            
            if not server or not email or not api_token:
                raise ValueError("Missing required environment variables: JIRA_SERVER, JIRA_EMAIL, JIRA_API_TOKEN")
            
            from jira.client import TokenAuth
            self.jira_client = JIRA(
                server=server,
                token_auth=api_token
            )
            logger.info("Successfully connected to Jira")
            
        except Exception as e:
            logger.error(f"Failed to initialize Jira client: {e}")
            raise

    async def _get_issue(self, issue_key: str) -> List[TextContent]:
        """Get detailed information about a Jira issue"""
        try:
            if not self.jira_client:
                return [TextContent(type="text", text="Jira client not initialized")]
            
            issue = self.jira_client.issue(issue_key)
            
            issue_data = {
                "key": issue.key,
                "summary": issue.fields.summary,
                "description": issue.fields.description or "No description",
                "status": issue.fields.status.name,
                "priority": issue.fields.priority.name if issue.fields.priority else "None",
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
                "reporter": issue.fields.reporter.displayName if issue.fields.reporter else "Unknown",
                "created": str(issue.fields.created),
                "updated": str(issue.fields.updated),
                "project": issue.fields.project.name,
                "issue_type": issue.fields.issuetype.name,
                "url": f"{self.jira_client.server_url}/browse/{issue.key}"
            }
            
            text = (f"**Issue: {issue_data['key']}**\n\n"
                   f"**Summary:** {issue_data['summary']}\n"
                   f"**Status:** {issue_data['status']}\n"
                   f"**Priority:** {issue_data['priority']}\n"
                   f"**Assignee:** {issue_data['assignee']}\n"
                   f"**Reporter:** {issue_data['reporter']}\n"
                   f"**Type:** {issue_data['issue_type']}\n"
                   f"**Project:** {issue_data['project']}\n"
                   f"**Created:** {issue_data['created']}\n"
                   f"**Updated:** {issue_data['updated']}\n"
                   f"**URL:** {issue_data['url']}\n\n"
                   f"**Description:**\n{issue_data['description']}")
            
            return [TextContent(type="text", text=text)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error fetching issue {issue_key}: {str(e)}")]

    async def _search_issues(self, jql: str, max_results: int = 50) -> List[TextContent]:
        """Search for issues using JQL"""
        try:
            issues = self.jira_client.search_issues(jql, maxResults=max_results)
            
            if not issues:
                return [TextContent(type="text", text="No issues found matching the query.")]
            
            result_text = f"**Found {len(issues)} issue(s):**\n\n"
            
            for issue in issues:
                result_text += (
                    f"• **{issue.key}** - {issue.fields.summary}\n"
                    f"  Status: {issue.fields.status.name} | "
                    f"Assignee: {issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned'}\n"
                    f"  URL: {self.jira_client.server_url}/browse/{issue.key}\n\n"
                )
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error searching issues: {str(e)}")]

    async def _create_issue(self, project_key: str, issue_type: str, summary: str, 
                          description: str, priority: str = "Medium") -> List[TextContent]:
        """Create a new Jira issue"""
        try:
            issue_dict = {
                'project': {'key': project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'name': issue_type},
            }
            
            # Add priority if specified
            if priority:
                issue_dict['priority'] = {'name': priority}
            
            new_issue = self.jira_client.create_issue(fields=issue_dict)
            
            text = (f"**Issue created successfully!**\n\n"
                   f"**Key:** {new_issue.key}\n"
                   f"**Summary:** {summary}\n"
                   f"**Type:** {issue_type}\n"
                   f"**Priority:** {priority}\n"
                   f"**URL:** {self.jira_client.server_url}/browse/{new_issue.key}")
            
            return [TextContent(type="text", text=text)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error creating issue: {str(e)}")]

    async def _update_issue(self, issue_key: str, summary: Optional[str] = None, 
                          description: Optional[str] = None) -> List[TextContent]:
        """Update an existing issue"""
        try:
            issue = self.jira_client.issue(issue_key)
            update_dict = {}
            
            if summary:
                update_dict['summary'] = summary
            if description:
                update_dict['description'] = description
                
            if not update_dict:
                return [TextContent(type="text", text="No fields specified for update.")]
            
            issue.update(fields=update_dict)
            
            updates = []
            if summary:
                updates.append(f"Summary: {summary}")
            if description:
                updates.append("Description updated")
                
            text = (f"**Issue {issue_key} updated successfully!**\n\n"
                   f"**Updated fields:** {', '.join(updates)}\n"
                   f"**URL:** {self.jira_client.server_url}/browse/{issue_key}")
            
            return [TextContent(type="text", text=text)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error updating issue {issue_key}: {str(e)}")]

    async def _add_comment(self, issue_key: str, comment: str) -> List[TextContent]:
        """Add a comment to an issue"""
        try:
            issue = self.jira_client.issue(issue_key)
            self.jira_client.add_comment(issue, comment)
            
            text = (f"**Comment added to {issue_key} successfully!**\n\n"
                   f"**Comment:** {comment}\n"
                   f"**URL:** {self.jira_client.server_url}/browse/{issue_key}")
            
            return [TextContent(type="text", text=text)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error adding comment to {issue_key}: {str(e)}")]

    async def _get_comments(self, issue_key: str) -> List[TextContent]:
        """Get all comments for an issue"""
        try:
            issue = self.jira_client.issue(issue_key)
            comments = self.jira_client.comments(issue)
            
            if not comments:
                return [TextContent(type="text", text=f"No comments found for issue {issue_key}.")]
            
            result_text = f"**Comments for {issue_key}:**\n\n"
            
            for comment in comments:
                result_text += (
                    f"**{comment.author.displayName}** - {comment.created}\n"
                    f"{comment.body}\n"
                    f"---\n\n"
                )
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error fetching comments for {issue_key}: {str(e)}")]

    async def _transition_issue(self, issue_key: str, transition_name: str) -> List[TextContent]:
        """Transition an issue to a new status"""
        try:
            issue = self.jira_client.issue(issue_key)
            transitions = self.jira_client.transitions(issue)
            
            # Find the transition by name
            transition_id = None
            available_transitions = []
            
            for transition in transitions:
                available_transitions.append(transition['name'])
                if transition['name'].lower() == transition_name.lower():
                    transition_id = transition['id']
                    break
            
            if not transition_id:
                text = (f"Transition '{transition_name}' not found for issue {issue_key}.\n\n"
                       f"Available transitions: {', '.join(available_transitions)}")
                return [TextContent(type="text", text=text)]
            
            self.jira_client.transition_issue(issue, transition_id)
            
            # Get updated issue to show new status
            updated_issue = self.jira_client.issue(issue_key)
            
            text = (f"**Issue {issue_key} transitioned successfully!**\n\n"
                   f"**New Status:** {updated_issue.fields.status.name}\n"
                   f"**URL:** {self.jira_client.server_url}/browse/{issue_key}")
            
            return [TextContent(type="text", text=text)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error transitioning issue {issue_key}: {str(e)}")]

    async def _get_project(self, project_key: str) -> List[TextContent]:
        """Get information about a project"""
        try:
            project = self.jira_client.project(project_key)
            
            project_data = {
                "key": project.key,
                "name": project.name,
                "description": getattr(project, 'description', 'No description'),
                "lead": project.lead.displayName if hasattr(project, 'lead') and project.lead else "No lead",
                "project_type": getattr(project, 'projectTypeKey', 'Unknown'),
                "url": f"{self.jira_client.server_url}/projects/{project.key}"
            }
            
            text = (f"**Project: {project_data['key']}**\n\n"
                   f"**Name:** {project_data['name']}\n"
                   f"**Lead:** {project_data['lead']}\n"
                   f"**Type:** {project_data['project_type']}\n"
                   f"**URL:** {project_data['url']}\n\n"
                   f"**Description:**\n{project_data['description']}")
            
            return [TextContent(type="text", text=text)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error fetching project {project_key}: {str(e)}")]

    async def _get_issue_types(self, project_key: str) -> List[TextContent]:
        """Get available issue types for a project"""
        try:
            project = self.jira_client.project(project_key)
            issue_types = project.issueTypes
            
            if not issue_types:
                return [TextContent(type="text", text=f"No issue types found for project {project_key}.")]
            
            result_text = f"**Issue types for project {project_key}:**\n\n"
            
            for issue_type in issue_types:
                result_text += f"• **{issue_type.name}**"
                if hasattr(issue_type, 'description') and issue_type.description:
                    result_text += f" - {issue_type.description}"
                result_text += "\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error fetching issue types for {project_key}: {str(e)}")]

    async def _get_my_issues(self, max_results: int = 20) -> List[TextContent]:
        """Get issues assigned to the current user"""
        try:
            jql = "assignee = currentUser() ORDER BY updated DESC"
            issues = self.jira_client.search_issues(jql, maxResults=max_results)
            
            if not issues:
                return [TextContent(type="text", text="No issues assigned to you found.")]
            
            result_text = f"**Your assigned issues ({len(issues)}):**\n\n"
            
            for issue in issues:
                result_text += (
                    f"• **{issue.key}** - {issue.fields.summary}\n"
                    f"  Status: {issue.fields.status.name} | "
                    f"Priority: {issue.fields.priority.name if issue.fields.priority else 'None'}\n"
                    f"  URL: {self.jira_client.server_url}/browse/{issue.key}\n\n"
                )
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error fetching your issues: {str(e)}")]

    async def _get_project_issues(self, project_key: str, max_results: int = 50) -> List[TextContent]:
        """Get all issues for a specific project"""
        try:
            jql = f"project = {project_key} ORDER BY updated DESC"
            issues = self.jira_client.search_issues(jql, maxResults=max_results)
            
            if not issues:
                return [TextContent(type="text", text=f"No issues found for project {project_key}.")]
            
            result_text = f"**Issues in project {project_key} ({len(issues)}):**\n\n"
            
            for issue in issues:
                result_text += (
                    f"• **{issue.key}** - {issue.fields.summary}\n"
                    f"  Status: {issue.fields.status.name} | "
                    f"Assignee: {issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned'}\n"
                    f"  URL: {self.jira_client.server_url}/browse/{issue.key}\n\n"
                )
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error fetching project issues: {str(e)}")]

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="jira-mcp-server",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(tools={}),
                ),
            )


async def main():
    """Main entry point"""
    server = JiraMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main()) 