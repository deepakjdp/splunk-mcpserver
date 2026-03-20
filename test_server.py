#!/usr/bin/env python3
"""
Test script for Splunk MCP Server
This script validates the server configuration and basic functionality.
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test if environment variables are properly configured."""
    print("Testing environment configuration...")
    load_dotenv()
    
    required_vars = [
        "SPLUNK_HOST",
        "SPLUNK_PORT",
        "SPLUNK_USERNAME",
        "SPLUNK_PASSWORD"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Mask password in output
            display_value = "***" if var == "SPLUNK_PASSWORD" else value
            print(f"  ✓ {var}: {display_value}")
    
    if missing_vars:
        print(f"\n  ✗ Missing environment variables: {', '.join(missing_vars)}")
        print("  Please create a .env file based on .env.example")
        return False
    
    print("  ✓ All required environment variables are set\n")
    return True


def test_imports():
    """Test if all required packages are installed."""
    print("Testing package imports...")
    
    packages = [
        ("fastmcp", "FastMCP"),
        ("splunklib.client", "Splunk SDK"),
        ("splunklib.results", "Splunk SDK Results"),
        ("dotenv", "python-dotenv")
    ]
    
    all_imported = True
    for package, name in packages:
        try:
            __import__(package)
            print(f"  ✓ {name} imported successfully")
        except ImportError as e:
            print(f"  ✗ Failed to import {name}: {e}")
            all_imported = False
    
    if not all_imported:
        print("\n  Please install required packages:")
        print("  pip install -r requirements.txt")
        return False
    
    print("  ✓ All packages imported successfully\n")
    return True


def test_splunk_connection():
    """Test connection to Splunk server."""
    print("Testing Splunk connection...")
    
    try:
        import splunklib.client as client
        load_dotenv()
        
        service = client.connect(
            host=os.getenv("SPLUNK_HOST", "localhost"),
            port=int(os.getenv("SPLUNK_PORT", "8089")),
            username=os.getenv("SPLUNK_USERNAME", "admin"),
            password=os.getenv("SPLUNK_PASSWORD", ""),
            scheme=os.getenv("SPLUNK_SCHEME", "https")
        )
        
        # Try to get server info
        info = service.info
        print(f"  ✓ Connected to Splunk server: {info.get('serverName', 'unknown')}")
        print(f"  ✓ Splunk version: {info.get('version', 'unknown')}")
        print(f"  ✓ License state: {info.get('licenseState', 'unknown')}\n")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed to connect to Splunk: {e}")
        print("  Please verify your Splunk credentials and server accessibility\n")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Splunk MCP Server - Configuration Test")
    print("=" * 60 + "\n")
    
    # Run tests
    env_ok = test_environment()
    imports_ok = test_imports()
    
    # Only test connection if environment and imports are OK
    connection_ok = False
    if env_ok and imports_ok:
        connection_ok = test_splunk_connection()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Environment Configuration: {'✓ PASS' if env_ok else '✗ FAIL'}")
    print(f"Package Imports: {'✓ PASS' if imports_ok else '✗ FAIL'}")
    print(f"Splunk Connection: {'✓ PASS' if connection_ok else '✗ FAIL' if env_ok and imports_ok else '⊘ SKIPPED'}")
    print("=" * 60 + "\n")
    
    if env_ok and imports_ok and connection_ok:
        print("✓ All tests passed! Your Splunk MCP Server is ready to use.")
        print("\nTo start the server, run:")
        print("  python server.py")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above before running the server.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
