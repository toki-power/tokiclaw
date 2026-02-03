# Installation Guide

## Prerequisites

1. **MCP Server Running**: Your Looker MCP server should be running at `http://127.0.0.1:5001/mcp/looker`

2. **Looker Credentials**: Set these environment variables:
   ```bash
   export LOOKER_BASE_URL="https://your-instance.looker.com"
   export LOOKER_CLIENT_ID="your-client-id"
   export LOOKER_CLIENT_SECRET="your-client-secret"
   ```

3. **Python Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Install the Skill

### Option 1: Add to OpenClaw Skills Directory

```bash
# Copy the skill to your skills directory
cp -r toki-looker-mcp-skill ~/Documents/openclaw/skills/

# Restart OpenClaw gateway
# (or it will auto-reload if watch is enabled)
```

### Option 2: Use as Workspace Skill

Add this directory to your workspace and OpenClaw will discover it automatically.

## Verify Installation

Test the MCP connection:

```bash
cd toki-looker-mcp-skill
python scripts/list_tools.py
```

You should see a list of available Looker tools from your MCP server.

## Usage Examples

### List LookML Models
```bash
python scripts/looker_models.py
```

### Explore a Model
```bash
python scripts/looker_explore.py toki_crm customers
```

### Run a Query
```bash
python scripts/looker_query.py toki_crm customers "customer.name,customer.status" --limit 100
```

### From OpenClaw Chat
Once installed, you can simply ask:
- "What Looker models are available?"
- "Show me the dimensions in the customers explore"
- "Run a Looker query for active customers"
- "Create a look showing revenue by month"

The skill will automatically use the MCP server to interact with Looker.

## MCP Server Configuration

Make sure your MCP server config includes the looker toolset:

```yaml
sources:
  toki_looker:
    kind: looker
    base_url: ${LOOKER_BASE_URL}
    client_id: ${LOOKER_CLIENT_ID}
    client_secret: ${LOOKER_CLIENT_SECRET}
    verify_ssl: true
    timeout: 600s

toolsets:
  looker:
    - looker_get_models
    - looker_get_explores
    - looker_get_dimensions
    - looker_get_measures
    - looker_get_filters
    - looker_get_parameters
    - looker_query
    - looker_query_sql
    - looker_query_url
    - looker_get_looks
    - looker_run_look
    - looker_make_look
    - looker_get_dashboards
    - looker_make_dashboard
    - looker_add_dashboard_element
```

## Troubleshooting

**"Connection refused"**
- Ensure MCP server is running: `curl http://127.0.0.1:5001/mcp/looker`
- Check MCP server logs

**"Module not found: requests"**
- Install dependencies: `pip install -r requirements.txt`

**"Authentication failed"**
- Verify LOOKER_CLIENT_ID and LOOKER_CLIENT_SECRET are set correctly
- Check that your API credentials have the necessary permissions

**"Tool not found"**
- Verify MCP server tools: `python scripts/list_tools.py`
- Ensure the `looker` toolset is enabled in your MCP config
