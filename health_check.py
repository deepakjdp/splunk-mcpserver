#!/usr/bin/env python3
"""
Health check script for deployed Splunk MCP Server
Tests the deployed server endpoint
"""

import sys
import requests
import argparse
from typing import Optional

def check_health(url: str, timeout: int = 10) -> bool:
    """
    Check if the server is healthy and responding.
    
    Args:
        url: Base URL of the deployed server
        timeout: Request timeout in seconds
    
    Returns:
        True if healthy, False otherwise
    """
    sse_url = f"{url}/sse" if not url.endswith("/sse") else url
    
    print(f"Checking health of: {sse_url}")
    print("=" * 60)
    
    try:
        # Test 1: Basic connectivity
        print("\n1. Testing connectivity...")
        response = requests.get(sse_url, timeout=timeout)
        
        if response.status_code == 200:
            print(f"   ✓ Server is reachable (Status: {response.status_code})")
        else:
            print(f"   ⚠ Unexpected status code: {response.status_code}")
        
        # Test 2: MCP protocol - list tools
        print("\n2. Testing MCP protocol...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        response = requests.post(
            sse_url,
            json=tools_request,
            headers={"Content-Type": "application/json"},
            timeout=timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result and "tools" in result["result"]:
                tool_count = len(result["result"]["tools"])
                print(f"   ✓ MCP protocol working ({tool_count} tools available)")
                
                # List tools
                print("\n   Available tools:")
                for tool in result["result"]["tools"]:
                    print(f"      - {tool.get('name', 'unknown')}")
                
                return True
            else:
                print(f"   ✗ Unexpected response format")
                print(f"   Response: {result}")
                return False
        else:
            print(f"   ✗ MCP protocol test failed (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"   ✗ Cannot connect to server: {e}")
        print(f"\n   Possible issues:")
        print(f"   - Server is not running")
        print(f"   - Incorrect URL")
        print(f"   - Network connectivity issues")
        return False
        
    except requests.exceptions.Timeout:
        print(f"   ✗ Request timed out after {timeout} seconds")
        print(f"\n   Possible issues:")
        print(f"   - Server is slow to respond")
        print(f"   - Server is under heavy load")
        print(f"   - Network latency issues")
        return False
        
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Health check for deployed Splunk MCP Server"
    )
    parser.add_argument(
        "url",
        help="Base URL of the deployed server (e.g., https://your-app.onrender.com)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)"
    )
    
    args = parser.parse_args()
    
    print("Splunk MCP Server - Health Check")
    print("=" * 60)
    
    is_healthy = check_health(args.url, args.timeout)
    
    print("\n" + "=" * 60)
    if is_healthy:
        print("✓ Health check PASSED - Server is healthy!")
        print("\nYour server is ready to use with MCP clients.")
        return 0
    else:
        print("✗ Health check FAILED - Server has issues")
        print("\nPlease check the server logs and configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
