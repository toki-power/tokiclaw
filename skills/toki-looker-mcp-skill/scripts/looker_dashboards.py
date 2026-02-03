#!/usr/bin/env python3
"""
Manage Looker Dashboards via MCP.
Usage:
  python looker_dashboards.py list [--title "search term"]
  python looker_dashboards.py create --title "My Dashboard" --description "Description"
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


def get_dashboards(title=None, limit=20):
    """Search for dashboards."""
    args = {"limit": limit}
    if title:
        args["title"] = title

    result = call_tool("looker_get_dashboards", args)
    return parse_response(result)


def create_dashboard(title, description=None):
    """Create a new dashboard."""
    args = {"title": title}
    if description:
        args["description"] = description

    result = call_tool("looker_make_dashboard", args)
    return parse_response(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Looker Dashboards via MCP")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # List command
    list_parser = subparsers.add_parser("list", help="List/search dashboards")
    list_parser.add_argument("--title", help="Search by title", default=None)
    list_parser.add_argument("--limit", type=int, help="Max results", default=20)

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a dashboard")
    create_parser.add_argument("--title", required=True, help="Dashboard title")
    create_parser.add_argument(
        "--description", help="Dashboard description", default=None
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "list":
            print("Searching dashboards...")
            if args.title:
                print(f"Title filter: {args.title}")
            print("=" * 50)

            dashboards = get_dashboards(title=args.title, limit=args.limit)

            if isinstance(dashboards, list):
                print(f"\nFound {len(dashboards)} dashboards:\n")
                for dash in dashboards:
                    dash_id = dash.get("id", "unknown")
                    title = dash.get("title", "Untitled")
                    folder = (
                        dash.get("folder", {}).get("name", "")
                        if dash.get("folder")
                        else ""
                    )
                    print(f"* [{dash_id}] {title}")
                    if folder:
                        print(f"  Folder: {folder}")
            else:
                print(json.dumps(dashboards, indent=2))

        elif args.command == "create":
            print(f"Creating dashboard: {args.title}")
            print("=" * 50)

            result = create_dashboard(args.title, args.description)
            print("\nDashboard created:")
            print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
