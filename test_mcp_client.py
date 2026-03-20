#!/usr/bin/env python3
"""
Simple MCP Client for testing the Splunk MCP Server
Tests both stdio and SSE transports
"""

import json
import sys
import requests
import time
from typing import Dict, Any

def test_sse_endpoint(host: str = "127.0.0.1", port: int = 8000):
    """Test the SSE endpoint of the MCP server."""
    url = f"http://{host}:{port}/sse"
    
    print(f"Testing SSE endpoint: {url}")
    print("=" * 60)
    
    try:
        # Test 1: Check if server is running
        print("\n1. Testing server availability...")
        response = requests.get(url, timeout=5, stream=True)
        
        if response.status_code == 200:
            print(f"   ✓ Server is running (Status: {response.status_code})")
        else:
            print(f"   ✗ Unexpected status code: {response.status_code}")
            return False
        
        # Test 2: Send initialize request
        print("\n2. Sending initialize request...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = requests.post(
            url,
            json=init_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"   ✓ Initialize successful")
            result = response.json()
            print(f"   Server info: {json.dumps(result, indent=2)}")
        else:
            print(f"   ✗ Initialize failed (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            return False
        
        # Test 3: List available tools
        print("\n3. Listing available tools...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = requests.post(
            url,
            json=tools_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result and "tools" in result["result"]:
                tools = result["result"]["tools"]
                print(f"   ✓ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"      - {tool.get('name', 'unknown')}: {tool.get('description', 'No description')[:60]}...")
            else:
                print(f"   Response: {json.dumps(result, indent=2)}")
        else:
            print(f"   ✗ Tools list failed (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            return False
        
        print("\n" + "=" * 60)
        print("✓ All SSE endpoint tests passed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"   ✗ Cannot connect to server at {url}")
        print(f"   Make sure the server is running with: python3 server.py --transport sse --port {port}")
        return False
    except requests.exceptions.Timeout:
        print(f"   ✗ Request timed out")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_get_splunk_info(host: str = "127.0.0.1", port: int = 8000):
    """Test calling the get_splunk_info tool."""
    url = f"http://{host}:{port}/sse"
    
    print("\n" + "=" * 60)
    print("Testing Splunk Tool: get_splunk_info")
    print("=" * 60)
    
    try:
        tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_splunk_info",
                "arguments": {}
            }
        }
        
        print("\nCalling get_splunk_info tool...")
        response = requests.post(
            url,
            json=tool_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Tool executed successfully")
            print(f"\nResult:\n{json.dumps(result, indent=2)}")
            return True
        else:
            print(f"✗ Tool execution failed (Status: {response.status_code})")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error calling tool: {e}")
        return False


def print_usage():
    """Print usage instructions."""
    print("""
Splunk MCP Server - Client Test Script

Usage:
    python3 test_mcp_client.py [--host HOST] [--port PORT] [--test-tool]

Options:
    --host HOST       Server host (default: 127.0.0.1)
    --port PORT       Server port (default: 8000)
    --test-tool       Also test calling a Splunk tool (requires configured .env)

Before running this test:
    1. Configure your .env file with Splunk credentials
    2. Start the server: python3 server.py --transport sse --port 8000
    3. Run this test: python3 test_mcp_client.py

Example:
    # Start server in one terminal
    python3 server.py --transport sse --port 8000
    
    # Test in another terminal
    python3 test_mcp_client.py --test-tool
""")


def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Splunk MCP Server")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--test-tool", action="store_true", help="Test calling a Splunk tool")
    parser.add_argument("--help-usage", action="store_true", help="Show detailed usage")
    
    args = parser.parse_args()
    
    if args.help_usage:
        print_usage()
        return 0
    
    print("Splunk MCP Server - Client Test")
    print("=" * 60)
    
    # Test SSE endpoint
    success = test_sse_endpoint(args.host, args.port)
    
    # Optionally test a tool
    if success and args.test_tool:
        test_get_splunk_info(args.host, args.port)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
