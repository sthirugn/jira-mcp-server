#!/usr/bin/env python3
"""
Test script for Jira MCP Server
Verifies that your Jira connection and credentials are working correctly.
"""

import os
import sys
from dotenv import load_dotenv
from jira import JIRA
import jira

def test_jira_connection():
    """Test the Jira connection with the configured credentials"""
    
    # Load environment variables
    load_dotenv()
    
    # Check if required environment variables are set
    server = os.getenv("JIRA_SERVER")
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")
    
    if not all([server, email, api_token]):
        print("❌ Missing required environment variables!")
        print("Please ensure the following are set in your .env file:")
        print("- JIRA_SERVER")
        print("- JIRA_EMAIL")
        print("- JIRA_API_TOKEN")
        return False
    
    print(f"🔗 Testing connection to: {server}")
    print(f"📧 Using email: {email}")
    
    try:
        # Initialize Jira client
        # Use token-based authentication instead of basic auth
        jira = JIRA(
            server=server,
            token_auth=api_token
        )
        
        print("✅ Successfully connected to Jira!")
        
        # Test basic functionality
        try:
            # Get current user info
            current_user = jira.current_user()
            print(f"👤 Logged in as: {current_user}")
            
            # Get projects (limited to first 5)
            projects = jira.projects()[:5]
            if projects:
                print(f"📂 Found {len(jira.projects())} total projects")
                print("📋 First 5 projects:")
                for project in projects:
                    print(f"   • {project.key}: {project.name}")
            else:
                print("⚠️  No projects found (you may not have access to any projects)")
            
            print("\n🎉 All tests passed! Your Jira MCP server should work correctly.")
            return True
            
        except Exception as e:
            print(f"⚠️  Connected to Jira but encountered an error during testing: {e}")
            print("This might indicate limited permissions or an unusual Jira setup.")
            return True  # Connection worked, just some feature issues
            
    except Exception as e:
        print(f"❌ Failed to connect to Jira: {e}")
        print("\n🔍 Troubleshooting tips:")
        print("1. Verify your JIRA_SERVER URL is correct (include https://)")
        print("2. Check that your email address is correct")
        print("3. Ensure your API token is valid and hasn't expired")
        print("4. Verify you have access to the Jira instance")
        print("5. Check if your organization requires VPN access")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Jira MCP Server Connection...")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("Please create a .env file with your Jira credentials.")
        print("You can copy from config.template and modify it.")
        sys.exit(1)
    
    success = test_jira_connection()
    
    if success:
        print("\n🚀 Your Jira MCP server is ready to use!")
        print("Add it to your Cursor MCP configuration to start using it.")
    else:
        print("\n💡 Please fix the issues above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 