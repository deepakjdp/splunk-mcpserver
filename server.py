#!/usr/bin/env python3
"""
Splunk MCP Server - FastMCP integration with Splunk
Provides tools to interact with Splunk for searching, querying, and managing data.
Supports both stdio and SSE transport protocols.
"""

import os
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime
import splunklib.client as client
import splunklib.results as results
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server with SSE support
mcp = FastMCP("Splunk MCP Server", dependencies=["splunk-sdk>=2.0.0"])

# Splunk connection configuration
SPLUNK_HOST = os.getenv("SPLUNK_HOST", "localhost")
SPLUNK_PORT = int(os.getenv("SPLUNK_PORT", "8089"))
SPLUNK_USERNAME = os.getenv("SPLUNK_USERNAME", "admin")
SPLUNK_PASSWORD = os.getenv("SPLUNK_PASSWORD", "")
SPLUNK_SCHEME = os.getenv("SPLUNK_SCHEME", "https")


def get_splunk_service():
    """Create and return a Splunk service connection."""
    try:
        service = client.connect(
            host=SPLUNK_HOST,
            port=SPLUNK_PORT,
            username=SPLUNK_USERNAME,
            password=SPLUNK_PASSWORD,
            scheme=SPLUNK_SCHEME
        )
        return service
    except Exception as e:
        raise Exception(f"Failed to connect to Splunk: {str(e)}")


@mcp.tool()
def search_splunk(
    query: str,
    earliest_time: str = "-24h",
    latest_time: str = "now",
    max_results: int = 100
) -> Dict[str, Any]:
    """
    Execute a Splunk search query and return results.
    
    Args:
        query: The Splunk search query (SPL - Search Processing Language)
        earliest_time: Start time for the search (default: -24h)
        latest_time: End time for the search (default: now)
        max_results: Maximum number of results to return (default: 100)
    
    Returns:
        Dictionary containing search results and metadata
    """
    try:
        service = get_splunk_service()
        
        # Create search job
        search_kwargs = {
            "earliest_time": earliest_time,
            "latest_time": latest_time,
            "max_count": max_results
        }
        
        job = service.jobs.create(query, **search_kwargs)
        
        # Wait for job to complete
        while not job.is_done():
            pass
        
        # Get results
        result_stream = job.results(output_mode="json", count=max_results)
        search_results = results.JSONResultsReader(result_stream)
        
        # Parse results
        events = []
        for result in search_results:
            if isinstance(result, dict):
                events.append(result)
        
        return {
            "success": True,
            "query": query,
            "event_count": len(events),
            "events": events,
            "search_id": job.sid,
            "earliest_time": earliest_time,
            "latest_time": latest_time
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }


@mcp.tool()
def list_splunk_indexes() -> Dict[str, Any]:
    """
    List all available Splunk indexes.
    
    Returns:
        Dictionary containing list of indexes with their properties
    """
    try:
        service = get_splunk_service()
        indexes = service.indexes
        
        index_list = []
        for index in indexes:
            index_list.append({
                "name": index.name,
                "total_event_count": index.totalEventCount,
                "current_db_size_mb": round(int(index.currentDBSizeMB), 2) if hasattr(index, 'currentDBSizeMB') else 0,
                "max_time": index.maxTime if hasattr(index, 'maxTime') else None,
                "min_time": index.minTime if hasattr(index, 'minTime') else None
            })
        
        return {
            "success": True,
            "index_count": len(index_list),
            "indexes": index_list
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_splunk_apps() -> Dict[str, Any]:
    """
    List all installed Splunk apps.
    
    Returns:
        Dictionary containing list of apps with their properties
    """
    try:
        service = get_splunk_service()
        apps = service.apps
        
        app_list = []
        for app in apps:
            app_list.append({
                "name": app.name,
                "label": app.label if hasattr(app, 'label') else app.name,
                "version": app.version if hasattr(app, 'version') else "unknown",
                "visible": app.visible if hasattr(app, 'visible') else True,
                "disabled": app.disabled if hasattr(app, 'disabled') else False
            })
        
        return {
            "success": True,
            "app_count": len(app_list),
            "apps": app_list
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_saved_searches() -> Dict[str, Any]:
    """
    List all saved searches in Splunk.
    
    Returns:
        Dictionary containing list of saved searches
    """
    try:
        service = get_splunk_service()
        saved_searches = service.saved_searches
        
        search_list = []
        for search in saved_searches:
            search_list.append({
                "name": search.name,
                "search": search.search if hasattr(search, 'search') else "",
                "is_scheduled": search.is_scheduled if hasattr(search, 'is_scheduled') else False,
                "cron_schedule": search.cron_schedule if hasattr(search, 'cron_schedule') else None
            })
        
        return {
            "success": True,
            "saved_search_count": len(search_list),
            "saved_searches": search_list
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def run_saved_search(search_name: str) -> Dict[str, Any]:
    """
    Execute a saved search by name.
    
    Args:
        search_name: Name of the saved search to execute
    
    Returns:
        Dictionary containing search results
    """
    try:
        service = get_splunk_service()
        saved_search = service.saved_searches[search_name]
        
        # Dispatch the saved search
        job = saved_search.dispatch()
        
        # Wait for job to complete
        while not job.is_done():
            pass
        
        # Get results
        result_stream = job.results(output_mode="json")
        search_results = results.JSONResultsReader(result_stream)
        
        # Parse results
        events = []
        for result in search_results:
            if isinstance(result, dict):
                events.append(result)
        
        return {
            "success": True,
            "search_name": search_name,
            "event_count": len(events),
            "events": events,
            "search_id": job.sid
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "search_name": search_name
        }


@mcp.tool()
def get_splunk_info() -> Dict[str, Any]:
    """
    Get Splunk server information and status.
    
    Returns:
        Dictionary containing Splunk server information
    """
    try:
        service = get_splunk_service()
        info = service.info
        
        return {
            "success": True,
            "server_name": info.get("serverName", "unknown"),
            "version": info.get("version", "unknown"),
            "build": info.get("build", "unknown"),
            "os_name": info.get("os_name", "unknown"),
            "cpu_arch": info.get("cpu_arch", "unknown"),
            "license_state": info.get("licenseState", "unknown"),
            "server_roles": info.get("server_roles", [])
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Splunk MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport protocol to use (default: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for SSE transport (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for SSE transport (default: 127.0.0.1)"
    )
    
    args = parser.parse_args()
    
    if args.transport == "sse":
        print(f"Starting Splunk MCP Server with SSE transport on {args.host}:{args.port}", file=sys.stderr)
        print(f"Connect your MCP client to: http://{args.host}:{args.port}/sse", file=sys.stderr)
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        print("Starting Splunk MCP Server with stdio transport", file=sys.stderr)
        mcp.run(transport="stdio")

# Made with Bob
