#!/usr/bin/env python3
"""
List LookML models from Looker via MCP.
Usage: python looker_models.py
"""

import json

import requests

MCP_URL = "http://127.0.0.1:5001/mcp/looker"


def send_mcp_request(method, params=None):
    """Send MCP request via JSON-RPC and get response."""
    request_data = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}

    response = requests.post(MCP_URL, json=request_data)
    response.raise_for_status()

    data = response.json()

    if "result" in data:
        return data["result"]
    elif "error" in data:
        raise Exception(f"MCP Error: {data['error']}")
    else:
        raise Exception(f"Unexpected response: {data}")


def call_tool(tool_name, arguments=None):
    """Call an MCP tool."""
    return send_mcp_request(
        "tools/call", {"name": tool_name, "arguments": arguments or {}}
    )


def get_models():
    """Get all LookML models."""
    result = call_tool("looker_get_models")

    # Extract content from MCP response
    if "content" in result and len(result["content"]) > 0:
        content = result["content"][0]
        if content["type"] == "text":
            return json.loads(content["text"])

    return result


if __name__ == "__main__":
    try:
        print("Fetching LookML models...")
        print("=" * 50)

        models = get_models()

        if isinstance(models, list):
            print(f"\nFound {len(models)} models:\n")
            for model in models:
                name = model.get("name", model.get("id", "unknown"))
                label = model.get("label", "")
                print(f"* {name}")
                if label and label != name:
                    print(f"  Label: {label}")
                if model.get("explores"):
                    print(f"  Explores: {len(model['explores'])}")
                print()
        else:
            print(json.dumps(models, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
