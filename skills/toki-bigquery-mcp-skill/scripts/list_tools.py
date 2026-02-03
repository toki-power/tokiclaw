#!/usr/bin/env python3
"""
List available tools from the MCP server.
Usage: python list_tools.py
"""

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

def list_tools():
    """List all available MCP tools."""
    return send_mcp_request("tools/list", {})

if __name__ == "__main__":
    try:
        print("Fetching available MCP tools...")
        print("=" * 50)
        tools = list_tools()
        
        if "tools" in tools:
            print(f"\nFound {len(tools['tools'])} tools:\n")
            for tool in tools['tools']:
                print(f"• {tool['name']}")
                if 'description' in tool:
                    print(f"  {tool['description']}")
                print()
        else:
            print(json.dumps(tools, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        print("\nTrying to call export_bigquery_data directly as a test...")
        try:
            test_result = send_mcp_request("tools/call", {
                "name": "export_bigquery_data",
                "arguments": {
                    "sql": "SELECT 1 as test",
                    "format": "csv"
                }
            })
            print("✓ export_bigquery_data tool works!")
            print(json.dumps(test_result, indent=2))
        except Exception as e2:
            print(f"Also failed: {e2}")
