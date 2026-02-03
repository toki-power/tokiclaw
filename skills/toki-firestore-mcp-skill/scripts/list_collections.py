#!/usr/bin/env python3
"""
List Firestore collections.
Usage: python list_collections.py [parent_path]

Examples:
  python list_collections.py                    # List root collections
  python list_collections.py users/user123      # List subcollections under a document
"""

import json
import os
import sys

import requests

MCP_URL = os.environ.get("MCP_URL", "http://127.0.0.1:5001/mcp/firestore")


def send_mcp_request(method, params=None):
    """Send MCP request via JSON-RPC and get response."""
    request_data = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}

    response = requests.post(MCP_URL, json=request_data)
    response.raise_for_status()

    if not response.text:
        raise Exception(f"Empty response from {MCP_URL}")

    data = response.json()

    if "result" in data:
        return data["result"]
    elif "error" in data:
        raise Exception(f"MCP Error: {data['error']}")
    else:
        raise Exception(f"Unexpected response: {data}")


def call_tool(tool_name, arguments):
    """Call an MCP tool with given arguments."""
    return send_mcp_request("tools/call", {"name": tool_name, "arguments": arguments})


def list_collections(parent_path=""):
    """List collections under a parent path."""
    args = {}
    if parent_path:
        args["parent"] = parent_path

    return call_tool("firestore_list_collections", args)


if __name__ == "__main__":
    parent = sys.argv[1] if len(sys.argv) > 1 else ""

    try:
        if parent:
            print(f"Listing collections under: {parent}")
        else:
            print("Listing root collections...")
        print("=" * 50)

        result = list_collections(parent)

        if "content" in result:
            for item in result["content"]:
                if item.get("type") == "text":
                    data = json.loads(item["text"])
                    if isinstance(data, list):
                        print(f"\nFound {len(data)} collections:\n")
                        for coll in data:
                            print(f"  - {coll}")
                    else:
                        print(json.dumps(data, indent=2))
        else:
            print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        print(f"\nUsing endpoint: {MCP_URL}")
