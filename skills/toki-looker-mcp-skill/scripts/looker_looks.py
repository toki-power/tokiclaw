#!/usr/bin/env python3
"""
Manage Looker Looks via MCP.
Usage:
  python looker_looks.py list [--title "search term"]
  python looker_looks.py run <look_id>
"""

import argparse
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


def get_looks(title=None, limit=20):
    """Search for looks."""
    args = {"limit": limit}
    if title:
        args["title"] = title

    result = call_tool("looker_get_looks", args)
    return parse_response(result)


def run_look(look_id):
    """Run a look and return data."""
    result = call_tool("looker_run_look", {"look_id": look_id})
    return parse_response(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Looker Looks via MCP")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # List command
    list_parser = subparsers.add_parser("list", help="List/search looks")
    list_parser.add_argument("--title", help="Search by title", default=None)
    list_parser.add_argument("--limit", type=int, help="Max results", default=20)

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a look")
    run_parser.add_argument("look_id", help="Look ID to run")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "list":
            print("Searching looks...")
            if args.title:
                print(f"Title filter: {args.title}")
            print("=" * 50)

            looks = get_looks(title=args.title, limit=args.limit)

            if isinstance(looks, list):
                print(f"\nFound {len(looks)} looks:\n")
                for look in looks:
                    look_id = look.get("id", "unknown")
                    title = look.get("title", "Untitled")
                    folder = look.get("folder", {}).get("name", "")
                    print(f"* [{look_id}] {title}")
                    if folder:
                        print(f"  Folder: {folder}")
            else:
                print(json.dumps(looks, indent=2))

        elif args.command == "run":
            print(f"Running look {args.look_id}...")
            print("=" * 50)

            data = run_look(args.look_id)

            if isinstance(data, list):
                print(f"\nResults ({len(data)} rows):\n")
                print(json.dumps(data[:10], indent=2))
                if len(data) > 10:
                    print(f"\n... and {len(data) - 10} more rows")
            else:
                print(json.dumps(data, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
