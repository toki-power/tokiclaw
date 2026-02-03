#!/usr/bin/env python3
"""
List BigQuery tables from the MCP server.
Usage: python list_tables.py
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

def list_tables():
    """List BigQuery tables."""
    result = send_mcp_request("tools/call", {
        "name": "list_bq_tables_sample",
        "arguments": {}
    })
    
    # Extract the text content from the MCP response
    if "content" in result and len(result["content"]) > 0:
        for item in result["content"]:
            if item["type"] == "text":
                print(item["text"])
    else:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    try:
        print("Fetching BigQuery tables...")
        print("=" * 50)
        list_tables()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
