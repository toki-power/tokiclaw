#!/usr/bin/env python3
"""
Explore a LookML model - list explores, dimensions, and measures.
Usage: python looker_explore.py <model_name> [explore_name]
"""

import json
import sys

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


def parse_response(result):
    """Extract content from MCP response."""
    if "content" in result and len(result["content"]) > 0:
        content = result["content"][0]
        if content["type"] == "text":
            return json.loads(content["text"])
    return result


def get_explores(model_name):
    """Get explores in a model."""
    result = call_tool("looker_get_explores", {"model_name": model_name})
    return parse_response(result)


def get_dimensions(model_name, explore_name):
    """Get dimensions in an explore."""
    result = call_tool(
        "looker_get_dimensions",
        {"model_name": model_name, "explore_name": explore_name},
    )
    return parse_response(result)


def get_measures(model_name, explore_name):
    """Get measures in an explore."""
    result = call_tool(
        "looker_get_measures", {"model_name": model_name, "explore_name": explore_name}
    )
    return parse_response(result)


def print_fields(fields, field_type):
    """Print a list of fields."""
    if isinstance(fields, list):
        print(f"\n{field_type} ({len(fields)}):")
        for field in fields[:20]:  # Limit output
            name = field.get("name", field.get("id", "unknown"))
            label = field.get("label", "")
            ftype = field.get("type", "")
            print(f"  - {name}")
            if label:
                print(f"    Label: {label}")
            if ftype:
                print(f"    Type: {ftype}")
        if len(fields) > 20:
            print(f"  ... and {len(fields) - 20} more")
    else:
        print(json.dumps(fields, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python looker_explore.py <model_name> [explore_name]")
        print("\nExamples:")
        print("  python looker_explore.py toki_crm")
        print("  python looker_explore.py toki_crm customers")
        sys.exit(1)

    model_name = sys.argv[1]
    explore_name = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        if explore_name:
            # Show details for specific explore
            print(f"Exploring {model_name}.{explore_name}")
            print("=" * 50)

            dimensions = get_dimensions(model_name, explore_name)
            print_fields(dimensions, "Dimensions")

            measures = get_measures(model_name, explore_name)
            print_fields(measures, "Measures")
        else:
            # List explores in model
            print(f"Explores in model: {model_name}")
            print("=" * 50)

            explores = get_explores(model_name)

            if isinstance(explores, list):
                print(f"\nFound {len(explores)} explores:\n")
                for explore in explores:
                    name = explore.get("name", explore.get("id", "unknown"))
                    label = explore.get("label", "")
                    print(f"* {name}")
                    if label and label != name:
                        print(f"  Label: {label}")
            else:
                print(json.dumps(explores, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
