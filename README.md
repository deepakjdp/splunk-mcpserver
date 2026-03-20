# Splunk MCP Server

A Model Context Protocol (MCP) server that provides integration with Splunk, enabling AI assistants to interact with Splunk for searching, querying, and managing data.

## Features

This MCP server provides the following tools for Splunk integration:

- **search_splunk**: Execute Splunk search queries (SPL) with customizable time ranges
- **list_splunk_indexes**: List all available Splunk indexes with metadata
- **get_splunk_apps**: Get information about installed Splunk apps
- **get_saved_searches**: List all saved searches in Splunk
- **run_saved_search**: Execute a saved search by name
- **get_splunk_info**: Get Splunk server information and status

## Prerequisites

- Python 3.8 or higher
- Access to a Splunk instance (Enterprise or Cloud)
- Splunk credentials with appropriate permissions

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Splunk credentials**:
   
   Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Splunk credentials:
   ```env
   SPLUNK_HOST=your-splunk-host.com
   SPLUNK_PORT=8089
   SPLUNK_USERNAME=your_username
   SPLUNK_PASSWORD=your_password
   SPLUNK_SCHEME=https
   ```

## Usage

### Running the Server

The server supports two transport protocols:

#### 1. stdio Transport (Default)

For use with Claude Desktop and other stdio-based MCP clients:

```bash
python server.py
# or explicitly
python server.py --transport stdio
```

#### 2. SSE Transport (Server-Sent Events)

For HTTP-based MCP clients and testing:

```bash
python server.py --transport sse --port 8000 --host 127.0.0.1
```

### Testing the Server

#### Test with MCP Client

A test client is provided to verify the SSE endpoint:

```bash
# Start the server in SSE mode (in one terminal)
python server.py --transport sse --port 8000

# Run the test client (in another terminal)
python test_mcp_client.py

# Test with Splunk tool execution (requires configured .env)
python test_mcp_client.py --test-tool
```

The test client will:
1. Check server availability
2. Send initialize request
3. List available tools
4. Optionally test calling a Splunk tool

#### Test with curl

You can also test the SSE endpoint with curl:

```bash
# Initialize connection
curl -X POST http://127.0.0.1:8000/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "test", "version": "1.0.0"}
    }
  }'

# List tools
curl -X POST http://127.0.0.1:8000/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'

# Call a tool
curl -X POST http://127.0.0.1:8000/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "get_splunk_info",
      "arguments": {}
    }
  }'
```

The SSE endpoint will be available at: `http://127.0.0.1:8000/sse`

**SSE Options:**
- `--transport sse`: Use SSE transport protocol
- `--port PORT`: Port number (default: 8000)
- `--host HOST`: Host address (default: 127.0.0.1)

### Using with Claude Desktop

To use this MCP server with Claude Desktop, add the following configuration to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "splunk": {
      "command": "python",
      "args": ["/path/to/splunk-mcpserver/server.py"],
      "env": {
        "SPLUNK_HOST": "your-splunk-host.com",
        "SPLUNK_PORT": "8089",
        "SPLUNK_USERNAME": "your_username",
        "SPLUNK_PASSWORD": "your_password",
        "SPLUNK_SCHEME": "https"
      }
    }
  }
}
```

Replace `/path/to/splunk-mcpserver/` with the actual path to this directory.

### Available Tools

#### 1. search_splunk

Execute a Splunk search query:

```python
search_splunk(
    query="search index=main error",
    earliest_time="-24h",
    latest_time="now",
    max_results=100
)
```

**Parameters**:
- `query` (required): SPL search query
- `earliest_time` (optional): Start time (default: "-24h")
- `latest_time` (optional): End time (default: "now")
- `max_results` (optional): Maximum results to return (default: 100)

#### 2. list_splunk_indexes

List all available indexes:

```python
list_splunk_indexes()
```

Returns information about all indexes including event counts and sizes.

#### 3. get_splunk_apps

Get installed Splunk apps:

```python
get_splunk_apps()
```

Returns list of apps with their versions and status.

#### 4. get_saved_searches

List all saved searches:

```python
get_saved_searches()
```

Returns saved searches with their queries and schedules.

#### 5. run_saved_search

Execute a saved search:

```python
run_saved_search(search_name="My Saved Search")
```

**Parameters**:
- `search_name` (required): Name of the saved search to execute

#### 6. get_splunk_info

Get Splunk server information:

```python
get_splunk_info()
```

Returns server version, build, OS, and license information.

## Example Queries

Here are some example Splunk queries you can use:

```spl
# Search for errors in the last hour
search index=main error earliest=-1h

# Count events by source type
index=main | stats count by sourcetype

# Search for failed login attempts
index=security action=failure | stats count by user

# Get top 10 error messages
index=main error | top 10 message

# Search with time range
search index=main earliest=-7d latest=now | timechart count by host
```

## Security Considerations

- **Never commit your `.env` file** to version control
- Use environment variables or secure credential management
- Ensure your Splunk user has appropriate permissions
- Use HTTPS (scheme=https) for production environments
- Consider using Splunk authentication tokens instead of passwords

## Troubleshooting

### Connection Issues

If you can't connect to Splunk:

1. Verify your Splunk instance is accessible
2. Check that port 8089 (management port) is open
3. Verify credentials are correct
4. Ensure SSL/TLS certificates are valid (or set `SPLUNK_SCHEME=http` for testing)

### Import Errors

If you see import errors, ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### Permission Errors

If you get permission errors:

1. Verify your Splunk user has search permissions
2. Check index-level permissions
3. Ensure the user can access saved searches

## Development

### Project Structure

```
splunk-mcpserver/
├── server.py           # Main MCP server implementation
├── requirements.txt    # Python dependencies
├── .env.example       # Example environment configuration
└── README.md          # This file
```

### Adding New Tools

To add new Splunk tools:

1. Define a new function with the `@mcp.tool()` decorator
2. Add proper type hints and docstrings
3. Implement error handling
4. Return structured data as dictionaries

Example:

```python
@mcp.tool()
def my_new_tool(param: str) -> Dict[str, Any]:
    """
    Description of what this tool does.
    
    Args:
        param: Description of parameter
    
    Returns:
        Dictionary containing results
    """
    try:
        service = get_splunk_service()
        # Your implementation here
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Resources

- [Splunk SDK for Python Documentation](https://dev.splunk.com/enterprise/docs/devtools/python/sdk-python/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Splunk Search Processing Language (SPL) Reference](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/)

## License

This project is provided as-is for educational and development purposes.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.