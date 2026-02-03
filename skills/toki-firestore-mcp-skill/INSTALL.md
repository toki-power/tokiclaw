# Installation Guide

## Prerequisites

1. **MCP Server Running**: Your Firestore MCP server should be running at `http://127.0.0.1:5001/mcp/firestore`

2. **Firestore Credentials**: Set these environment variables:
   ```bash
   export FIRESTORE_PROJECT="your-gcp-project-id"
   export FIRESTORE_DATABASE=""  # optional, empty for (default) database
   ```

3. **Google Cloud Authentication**: Ensure you have valid credentials:
   ```bash
   # Option 1: Application Default Credentials
   gcloud auth application-default login
   
   # Option 2: Service Account Key
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
   ```

4. **Python Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Install the Skill

### Option 1: Add to OpenClaw Skills Directory

```bash
# Copy the skill to your skills directory
cp -r toki-firestore-mcp-skill ~/Documents/openclaw/skills/

# Restart OpenClaw gateway
# (or it will auto-reload if watch is enabled)
```

### Option 2: Use as Workspace Skill

Add this directory to your workspace and OpenClaw will discover it automatically.

## Verify Installation

Test the MCP connection:

```bash
cd toki-firestore-mcp-skill
python scripts/list_tools.py
```

You should see a list of available Firestore tools from your MCP server.

## Usage Examples

### List Root Collections
```bash
python scripts/list_collections.py
```

### Get Documents
```bash
python scripts/get_documents.py "users/user123"
```

### Query a Collection
```bash
python scripts/query_collection.py "users"
```

### From OpenClaw Chat
Once installed, you can simply ask:
- "What collections are in Firestore?"
- "Get the document at users/abc123"
- "Query the orders collection for status=pending"
- "Add a new user document"

The skill will automatically use the MCP server to interact with Firestore.

## MCP Server Configuration

Make sure your MCP server config includes the firestore toolset:

```yaml
sources:
  toki_firestore:
    kind: firestore
    project: ${FIRESTORE_PROJECT}
    database: ${FIRESTORE_DATABASE:}

toolsets:
  firestore:
    - firestore_get_documents
    - firestore_add_documents
    - firestore_list_collections
    - firestore_query_collection
    # Uncomment if needed:
    # - firestore_update_document
    # - firestore_delete_documents
    # - firestore_get_rules
    # - firestore_validate_rules
```

## Troubleshooting

**"Connection refused"**
- Ensure MCP server is running: `curl http://127.0.0.1:5001/mcp/firestore`
- Check MCP server logs

**"Module not found: requests"**
- Install dependencies: `pip install -r requirements.txt`

**"Authentication failed"**
- Verify FIRESTORE_PROJECT is set correctly
- Check Google Cloud credentials are configured
- Ensure service account has Firestore permissions

**"Permission denied"**
- Check Firestore security rules in Firebase Console
- Verify IAM roles for your service account

**"Tool not found"**
- Verify MCP server tools: `python scripts/list_tools.py`
- Ensure the `firestore` toolset is enabled in your MCP config
