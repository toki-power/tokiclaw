#!/usr/bin/env python3
"""
Run a Looker query via MCP.
Usage: python looker_query.py <model> <explore> <fields> [options]

Examples:
  python looker_query.py toki_crm customers "customer.name,customer.status"
  python looker_query.py toki_crm customers "customer.name,customer.count" --limit 100
  python looker_query.py toki_crm customers "customer.name" --filters '{"customer.status":"Active"}'
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


def run_query(model_id, explore_name, fields, filters=None, sorts=None, limit=None):
    """Run a Looker query."""
    args = {
        "model_id": model_id,
        "explore_name": explore_name,
        "fields": fields if isinstance(fields, list) else fields.split(","),
    }

    if filters:
        args["filters"] = filters
    if sorts:
        args["sorts"] = sorts if isinstance(sorts, list) else sorts.split(",")
    if limit:
        args["row_limit"] = limit

    result = call_tool("looker_query", args)
    return parse_response(result)


def get_query_sql(model_id, explore_name, fields, filters=None):
    """Get the SQL for a Looker query."""
    args = {
        "model_id": model_id,
        "explore_name": explore_name,
        "fields": fields if isinstance(fields, list) else fields.split(","),
    }

    if filters:
        args["filters"] = filters

    result = call_tool("looker_query_sql", args)
    return parse_response(result)


def get_query_url(model_id, explore_name, fields, filters=None):
    """Get the Looker URL for a query."""
    args = {
        "model_id": model_id,
        "explore_name": explore_name,
        "fields": fields if isinstance(fields, list) else fields.split(","),
    }

    if filters:
        args["filters"] = filters

    result = call_tool("looker_query_url", args)
    return parse_response(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Looker query via MCP")
    parser.add_argument("model", help="LookML model name")
    parser.add_argument("explore", help="Explore name")
    parser.add_argument("fields", help="Comma-separated list of fields")
    parser.add_argument("--filters", help="JSON object of filters", default=None)
    parser.add_argument(
        "--sorts", help="Comma-separated list of sort fields", default=None
    )
    parser.add_argument("--limit", type=int, help="Row limit", default=None)
    parser.add_argument(
        "--sql", action="store_true", help="Show generated SQL instead of running query"
    )
    parser.add_argument(
        "--url", action="store_true", help="Show Looker URL instead of running query"
    )

    args = parser.parse_args()

    filters = json.loads(args.filters) if args.filters else None

    try:
        if args.sql:
            print("Generated SQL:")
            print("=" * 50)
            sql = get_query_sql(args.model, args.explore, args.fields, filters)
            print(sql)
        elif args.url:
            print("Looker URL:")
            print("=" * 50)
            url = get_query_url(args.model, args.explore, args.fields, filters)
            print(url)
        else:
            print(f"Running query: {args.model}.{args.explore}")
            print(f"Fields: {args.fields}")
            if filters:
                print(f"Filters: {filters}")
            print("=" * 50)

            data = run_query(
                args.model,
                args.explore,
                args.fields,
                filters=filters,
                sorts=args.sorts,
                limit=args.limit,
            )

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
