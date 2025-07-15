#!/usr/bin/env python3
"""
Setup script for Jira MCP Server
Helps users install dependencies and configure the server.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path(".env")
    template_file = Path("config.template")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
        
    if not template_file.exists():
        print("❌ config.template file not found")
        return False
        
    try:
        with open(template_file, 'r') as template:
            content = template.read()
        
        with open(env_file, 'w') as env:
            env.write(content)
        
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your actual Jira credentials!")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Jira MCP Server...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        sys.exit(1)
    
    # Make server.py executable
    server_file = Path("server.py")
    if server_file.exists():
        os.chmod(server_file, 0o755)
        print("✅ Made server.py executable")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Edit .env file with your Jira credentials")
    print("2. Add the server to your Cursor MCP configuration")
    print("3. Test the connection by running: python server.py")
    print("\nSee README.md for detailed configuration instructions.")

if __name__ == "__main__":
    main() 