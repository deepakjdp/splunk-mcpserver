# Quick Start Guide - Splunk MCP Server

This guide will help you get the Splunk MCP Server up and running quickly.

## Prerequisites

- Python 3.8 or higher
- Access to a Splunk instance
- Splunk credentials (username and password)

## Installation Steps

### 1. Install Xcode Command Line Tools (macOS only)

If you're on macOS and haven't installed Xcode Command Line Tools:

```bash
xcode-select --install
```

Follow the prompts to complete the installation.

### 2. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

This will install:
- FastMCP (MCP server framework)
- Splunk SDK for Python
- python-dotenv (environment variable management)
- pydantic (data validation)
- requests (HTTP client for testing)

### 3. Configure Splunk Credentials

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your Splunk details:

```env
SPLUNK_HOST=your-splunk-host.com
SPLUNK_PORT=8089
SPLUNK_USERNAME=admin
SPLUNK_PASSWORD=your_password
SPLUNK_SCHEME=https
```

**Important:** Never commit the `.env` file to version control!

### 4. Test Your Configuration

Run the configuration test:

```bash
python3 test_server.py
```

This will verify:
- Environment variables are set
- All packages are installed
- Connection to Splunk works

## Running the Server

### Option 1: stdio Transport (for Claude Desktop)

```bash
python3 server.py
```

### Option 2: SSE Transport (for HTTP clients)

```bash
python3 server.py --transport sse --port 8000
```

The server will be available at: `http://127.0.0.1:8000/sse`

## Testing the Server

### Test with the provided client

In one terminal, start the server:

```bash
python3 server.py --transport sse --port 8000
```

In another terminal, run the test client:

```bash
python3 test_mcp_client.py
```

To test with actual Splunk tool execution:

```bash
python3 test_mcp_client.py --test-tool
```

### Test with curl

```bash
# List available tools
curl -X POST http://127.0.0.1:8000/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

## Using with Claude Desktop

1. Open Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the Splunk MCP server configuration:

```json
{
  "mcpServers": {
    "splunk": {
      "command": "python3",
      "args": ["/full/path/to/splunk-mcpserver/server.py"],
      "env": {
        "SPLUNK_HOST": "your-splunk-host.com",
        "SPLUNK_PORT": "8089",
        "SPLUNK_USERNAME": "admin",
        "SPLUNK_PASSWORD": "your_password",
        "SPLUNK_SCHEME": "https"
      }
    }
  }
}
```

3. Restart Claude Desktop

4. The Splunk tools will now be available in Claude!

## Available Tools

Once connected, you can use these tools:

1. **search_splunk** - Execute SPL queries
   ```
   Search for errors in the last hour: search index=main error earliest=-1h
   ```

2. **list_splunk_indexes** - List all indexes
   ```
   Show me all available Splunk indexes
   ```

3. **get_splunk_apps** - Get installed apps
   ```
   What Splunk apps are installed?
   ```

4. **get_saved_searches** - List saved searches
   ```
   Show me all saved searches
   ```

5. **run_saved_search** - Execute a saved search
   ```
   Run the saved search named "Daily Error Report"
   ```

6. **get_splunk_info** - Get server information
   ```
   What version of Splunk is running?
   ```

## Example Queries

Here are some example Splunk queries you can try:

```spl
# Search for errors in the last 24 hours
search index=main error earliest=-24h

# Count events by source type
index=main | stats count by sourcetype

# Search for failed login attempts
index=security action=failure | stats count by user

# Get top 10 error messages
index=main error | top 10 message

# Time chart of events by host
search index=main earliest=-7d | timechart count by host
```

## Troubleshooting

### Cannot connect to Splunk

- Verify your Splunk instance is accessible
- Check that port 8089 (management port) is open
- Verify credentials are correct
- Try using `SPLUNK_SCHEME=http` for testing (not recommended for production)

### Import errors

Make sure all dependencies are installed:

```bash
pip3 install -r requirements.txt
```

### Permission errors

- Verify your Splunk user has search permissions
- Check index-level permissions
- Ensure the user can access saved searches

### Server won't start

- Check if another process is using the port
- Try a different port: `python3 server.py --transport sse --port 8001`
- Check the error messages in the console

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the [Splunk SPL Reference](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/)
- Check out [FastMCP documentation](https://github.com/jlowin/fastmcp)
- Learn about [Model Context Protocol](https://modelcontextprotocol.io/)

## Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review the error messages carefully
3. Verify your Splunk credentials and connectivity
4. Check the Splunk server logs
5. Ensure all dependencies are properly installed

## Security Best Practices

- Never commit `.env` file to version control
- Use strong passwords for Splunk accounts
- Use HTTPS (scheme=https) in production
- Consider using Splunk authentication tokens instead of passwords
- Limit Splunk user permissions to only what's needed
- Regularly rotate credentials