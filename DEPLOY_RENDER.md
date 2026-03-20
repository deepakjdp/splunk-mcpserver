# Deploying Splunk MCP Server to Render

This guide walks you through deploying the Splunk MCP Server to Render.com.

## Prerequisites

- A [Render.com](https://render.com) account (free tier available)
- A GitHub account
- Access to a Splunk instance
- Splunk credentials (host, username, password)

## Deployment Steps

### Step 1: Prepare Your Repository

1. **Initialize Git repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Splunk MCP Server"
   ```

2. **Create a GitHub repository**:
   - Go to [GitHub](https://github.com/new)
   - Create a new repository (e.g., `splunk-mcp-server`)
   - Don't initialize with README (we already have one)

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/splunk-mcp-server.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Render

#### Option A: Using render.yaml (Recommended)

1. **Log in to Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Sign in or create an account

2. **Create New Blueprint**:
   - Click "New +" → "Blueprint"
   - Connect your GitHub account if not already connected
   - Select your `splunk-mcp-server` repository
   - Render will automatically detect the `render.yaml` file

3. **Configure Environment Variables**:
   - Render will prompt you to set the following variables:
     - `SPLUNK_HOST`: Your Splunk server hostname (e.g., `splunk.example.com`)
     - `SPLUNK_USERNAME`: Your Splunk username
     - `SPLUNK_PASSWORD`: Your Splunk password (will be encrypted)
   
4. **Deploy**:
   - Click "Apply" to start the deployment
   - Wait for the build and deployment to complete (usually 2-5 minutes)

#### Option B: Manual Setup

1. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name**: `splunk-mcp-server`
     - **Region**: Choose closest to your Splunk instance
     - **Branch**: `main`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python server.py --transport sse --port $PORT --host 0.0.0.0`

2. **Set Environment Variables**:
   Go to "Environment" tab and add:
   ```
   PYTHON_VERSION=3.11.0
   SPLUNK_HOST=your-splunk-host.com
   SPLUNK_PORT=8089
   SPLUNK_USERNAME=your_username
   SPLUNK_PASSWORD=your_password
   SPLUNK_SCHEME=https
   ```

3. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment to complete

### Step 3: Verify Deployment

1. **Check Service Status**:
   - In Render dashboard, check that service status is "Live"
   - View logs to ensure no errors

2. **Get Your Service URL**:
   - Your service will be available at: `https://your-service-name.onrender.com`
   - The SSE endpoint will be: `https://your-service-name.onrender.com/sse`

3. **Test the Endpoint**:
   ```bash
   # Test with curl
   curl -X POST https://your-service-name.onrender.com/sse \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "id": 1,
       "method": "tools/list",
       "params": {}
     }'
   ```

### Step 4: Use with MCP Clients

#### With Claude Desktop

Update your Claude Desktop config to use the deployed server:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "splunk": {
      "url": "https://your-service-name.onrender.com/sse",
      "transport": "sse"
    }
  }
}
```

#### With Custom MCP Client

```python
import requests

url = "https://your-service-name.onrender.com/sse"

# List tools
response = requests.post(
    url,
    json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
)
print(response.json())
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SPLUNK_HOST` | Yes | - | Splunk server hostname |
| `SPLUNK_PORT` | No | 8089 | Splunk management port |
| `SPLUNK_USERNAME` | Yes | - | Splunk username |
| `SPLUNK_PASSWORD` | Yes | - | Splunk password |
| `SPLUNK_SCHEME` | No | https | Protocol (http/https) |
| `PORT` | No | 8000 | Server port (auto-set by Render) |

### Updating Environment Variables

1. Go to your service in Render dashboard
2. Click "Environment" tab
3. Update variables
4. Service will automatically redeploy

## Monitoring

### View Logs

1. Go to your service in Render dashboard
2. Click "Logs" tab
3. View real-time logs

### Health Checks

Render automatically performs health checks on the `/sse` endpoint.

### Metrics

- View request metrics in Render dashboard
- Monitor response times and error rates
- Set up alerts for downtime

## Troubleshooting

### Deployment Fails

**Check build logs**:
- Ensure all dependencies in `requirements.txt` are valid
- Verify Python version compatibility

**Common issues**:
- Missing environment variables
- Invalid Splunk credentials
- Network connectivity to Splunk instance

### Service Won't Start

**Check start command**:
```bash
python server.py --transport sse --port $PORT --host 0.0.0.0
```

**Verify environment variables**:
- All required variables are set
- No typos in variable names

### Cannot Connect to Splunk

**Verify Splunk accessibility**:
- Splunk instance is accessible from Render's network
- Port 8089 is open
- Credentials are correct
- SSL/TLS certificates are valid

**Firewall rules**:
- Render's IP ranges may need to be whitelisted
- Check Splunk firewall settings

### 502 Bad Gateway

**Possible causes**:
- Server crashed (check logs)
- Port binding issue
- Health check failing

**Solutions**:
- Check logs for errors
- Verify start command
- Ensure server binds to `0.0.0.0` not `127.0.0.1`

## Performance Optimization

### Free Tier Limitations

Render's free tier:
- Service spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- 750 hours/month of runtime

### Upgrade Options

For production use, consider:
- **Starter Plan** ($7/month): No spin-down, better performance
- **Standard Plan** ($25/month): More resources, better reliability

### Caching

Consider implementing caching for frequently accessed Splunk data:
- Use Redis for caching search results
- Cache index lists and app information
- Set appropriate TTLs

## Security Best Practices

### Environment Variables

- Never commit `.env` file
- Use Render's encrypted environment variables
- Rotate credentials regularly

### Network Security

- Use HTTPS for all connections
- Verify SSL certificates
- Use Splunk authentication tokens instead of passwords when possible

### Access Control

- Limit Splunk user permissions
- Use read-only accounts when possible
- Monitor access logs

## Continuous Deployment

### Automatic Deploys

Render automatically deploys when you push to your main branch:

```bash
git add .
git commit -m "Update server"
git push origin main
```

### Manual Deploys

In Render dashboard:
1. Go to your service
2. Click "Manual Deploy"
3. Select branch
4. Click "Deploy"

### Rollback

To rollback to a previous version:
1. Go to "Events" tab
2. Find the previous successful deploy
3. Click "Rollback to this version"

## Cost Estimation

### Free Tier
- **Cost**: $0/month
- **Limitations**: Spins down after inactivity
- **Best for**: Development, testing, personal use

### Starter Tier
- **Cost**: $7/month
- **Features**: Always on, better performance
- **Best for**: Small teams, light production use

### Standard Tier
- **Cost**: $25/month
- **Features**: More resources, better reliability
- **Best for**: Production use, multiple users

## Support

### Render Support
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com/)
- [Render Status](https://status.render.com/)

### Project Support
- Check [README.md](README.md) for general documentation
- Review [QUICKSTART.md](QUICKSTART.md) for setup help
- Check GitHub issues for known problems

## Next Steps

After deployment:
1. Test all Splunk tools
2. Set up monitoring and alerts
3. Configure Claude Desktop or your MCP client
4. Document your Splunk queries and use cases
5. Consider upgrading to paid tier for production use

## Additional Resources

- [Render Python Documentation](https://render.com/docs/deploy-python)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Splunk SDK Documentation](https://dev.splunk.com/enterprise/docs/devtools/python/sdk-python/)
- [Model Context Protocol](https://modelcontextprotocol.io/)