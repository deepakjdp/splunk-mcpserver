#!/usr/bin/env python3
"""
Structure validation script for Splunk MCP Server
Validates the project structure and code syntax without requiring dependencies.
"""

import os
import sys
import ast

def check_file_exists(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print(f"  ✓ {description}: {filepath}")
        return True
    else:
        print(f"  ✗ {description} not found: {filepath}")
        return False

def validate_python_syntax(filepath):
    """Validate Python file syntax."""
    try:
        with open(filepath, 'r') as f:
            code = f.read()
            ast.parse(code)
        print(f"  ✓ Valid Python syntax: {filepath}")
        return True
    except SyntaxError as e:
        print(f"  ✗ Syntax error in {filepath}: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error reading {filepath}: {e}")
        return False

def count_mcp_tools(filepath):
    """Count the number of MCP tools defined in server.py."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            tool_count = content.count('@mcp.tool()')
        print(f"  ✓ Found {tool_count} MCP tools defined")
        return tool_count
    except Exception as e:
        print(f"  ✗ Error analyzing tools: {e}")
        return 0

def main():
    """Run validation checks."""
    print("=" * 60)
    print("Splunk MCP Server - Structure Validation")
    print("=" * 60 + "\n")
    
    print("Checking project files...")
    files_ok = all([
        check_file_exists("server.py", "Main server file"),
        check_file_exists("requirements.txt", "Requirements file"),
        check_file_exists(".env.example", "Environment template"),
        check_file_exists("README.md", "Documentation"),
        check_file_exists(".gitignore", "Git ignore file"),
        check_file_exists("test_server.py", "Test script")
    ])
    print()
    
    print("Validating Python syntax...")
    syntax_ok = all([
        validate_python_syntax("server.py"),
        validate_python_syntax("test_server.py")
    ])
    print()
    
    print("Analyzing MCP tools...")
    tool_count = count_mcp_tools("server.py")
    tools_ok = tool_count >= 6
    print()
    
    print("Checking requirements.txt content...")
    try:
        with open("requirements.txt", 'r') as f:
            requirements = f.read()
            required_packages = ["fastmcp", "splunk-sdk", "python-dotenv", "pydantic"]
            missing = [pkg for pkg in required_packages if pkg not in requirements]
            if not missing:
                print(f"  ✓ All required packages listed: {', '.join(required_packages)}")
                reqs_ok = True
            else:
                print(f"  ✗ Missing packages: {', '.join(missing)}")
                reqs_ok = False
    except Exception as e:
        print(f"  ✗ Error reading requirements.txt: {e}")
        reqs_ok = False
    print()
    
    print("=" * 60)
    print("Validation Summary")
    print("=" * 60)
    print(f"Project Files: {'✓ PASS' if files_ok else '✗ FAIL'}")
    print(f"Python Syntax: {'✓ PASS' if syntax_ok else '✗ FAIL'}")
    print(f"MCP Tools ({tool_count}): {'✓ PASS' if tools_ok else '✗ FAIL'}")
    print(f"Requirements: {'✓ PASS' if reqs_ok else '✗ FAIL'}")
    print("=" * 60 + "\n")
    
    if all([files_ok, syntax_ok, tools_ok, reqs_ok]):
        print("✓ Structure validation passed!")
        print("\nNext steps:")
        print("1. Install Xcode Command Line Tools (if prompted)")
        print("2. Install dependencies: pip3 install -r requirements.txt")
        print("3. Configure .env file with your Splunk credentials")
        print("4. Run: python3 test_server.py")
        print("5. Start server: python3 server.py")
        return 0
    else:
        print("✗ Some validation checks failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
