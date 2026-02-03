#!/usr/bin/env python3
"""
Execute BigQuery queries via MCP JSON-RPC server.
Usage: python mcp_query.py "SELECT * FROM table" [format]
       python mcp_query.py "SELECT * FROM table" csv
       python mcp_query.py "SELECT * FROM table" json
"""

import sys
import json
import requests

MCP_URL = "http://127.0.0.1:5001/mcp/default"

def send_mcp_request(method, params=None):
    """Send MCP request via JSON-RPC and get response."""
    request_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    
    response = requests.post(MCP_URL, json=request_data)
    response.raise_for_status()
    
    data = response.json()
    
    if "result" in data:
        return data["result"]
    elif "error" in data:
        raise Exception(f"MCP Error: {data['error']}")
    else:
        raise Exception(f"Unexpected response: {data}")

def call_tool(tool_name, arguments):
    """Call an MCP tool."""
    return send_mcp_request("tools/call", {
        "name": tool_name,
        "arguments": arguments
    })

def query_bigquery(sql, format="csv"):
    """Execute a BigQuery SQL query and export results."""
    result = call_tool("export_bigquery_data", {
        "sql": sql,
        "format": format
    })
    
    # Extract the text content from the MCP response
    if "content" in result and len(result["content"]) > 0:
        content = result["content"][0]
        if content["type"] == "text":
            return json.loads(content["text"])
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mcp_query.py 'SELECT ...' [format]")
        print("Formats: csv (default), json, parquet")
        sys.exit(1)
    
    sql = sys.argv[1]
    format = sys.argv[2] if len(sys.argv) > 2 else "csv"
    
    try:
        result = query_bigquery(sql, format)
        print(json.dumps(result, indent=2))
        
        # If successful, also show download URL
        if result.get("success") and result.get("download_url"):
            print(f"\n✓ Export ready: {result['download_url']}")
            print(f"  Rows: {result.get('row_count', 'unknown')}")
            print(f"  Size: {result.get('file_size_bytes', 'unknown')} bytes")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
