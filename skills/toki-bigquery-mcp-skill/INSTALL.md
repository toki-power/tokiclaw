# Installation Guide

## Prerequisites

1. **MCP Server Running**: Your BigQuery MCP server should be running at `http://127.0.0.1:5001/mcp/sse`

2. **Python Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Install the Skill

### Option 1: Add to OpenClaw Skills Directory

```bash
# Copy the skill to your skills directory
cp -r toki-bigquery-mcp-skill ~/Documents/openclaw/skills/

# Restart OpenClaw gateway
# (or it will auto-reload if watch is enabled)
```

### Option 2: Use as Workspace Skill

Add this directory to your workspace and OpenClaw will discover it automatically.

## Verify Installation

Test the MCP connection:

```bash
cd toki-bigquery-mcp-skill
python scripts/list_tools.py
```

You should see a list of available BigQuery tools from your MCP server.

## Usage Examples

### Query BigQuery
```bash
python scripts/mcp_query.py "SELECT COUNT(*) FROM users"
```

### From OpenClaw Chat
Once installed, you can simply ask:
- "How many users do we have?"
- "Query BigQuery for today's revenue"
- "Show me the top 10 customers"

The skill will automatically use the MCP server to execute queries.

## Troubleshooting

**"Connection refused"**
- Ensure MCP server is running: `curl http://127.0.0.1:5001/mcp/sse`
- Check MCP server logs

**"Module not found: sseclient"**
- Install dependencies: `pip install -r requirements.txt`

**"Tool not found"**
- Verify MCP server tools: `python scripts/list_tools.py`
- Check that your MCP server is properly configured
