#!/usr/bin/env python3
"""
List available tools from the Firestore MCP server.
Usage: python list_tools.py
       MCP_URL=http://127.0.0.1:5001/mcp/firestore python list_tools.py
"""

import json
import os

import requests

# MCP endpoint - override with MCP_URL env var if needed
MCP_URL = os.environ.get("MCP_URL", "http://127.0.0.1:5001/mcp/firestore")


def send_mcp_request(method, params=None):
    """Send MCP request via JSON-RPC and get response."""
    request_data = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}

    response = requests.post(MCP_URL, json=request_data)
    response.raise_for_status()

    # Check for empty response
    if not response.text:
        raise Exception(f"Empty response from {MCP_URL} - endpoint may not exist")

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
        print("Fetching available Firestore MCP tools...")
        print("=" * 50)
        tools = list_tools()

        if "tools" in tools:
            print(f"\nFound {len(tools['tools'])} tools:\n")
            for tool in tools["tools"]:
                print(f"* {tool['name']}")
                if "description" in tool:
                    desc = tool["description"].split("\n")[0]  # First line only
                    print(f"  {desc}")
                print()
        else:
            print(json.dumps(tools, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        print(f"\nUsing endpoint: {MCP_URL}")
        print("\nTry these endpoints:")
        print("  MCP_URL=http://127.0.0.1:5001/mcp/firestore python list_tools.py")
        print("  MCP_URL=http://127.0.0.1:5001/mcp/default python list_tools.py")
        print(
            "\nMake sure the MCP server is running with the firestore toolset enabled."
        )
