#!/usr/bin/env python3
"""
Query a Firestore collection with optional filters.
Usage: python query_collection.py <collection> [--where field=value] [--limit N]

Examples:
  python query_collection.py users
  python query_collection.py users --limit 10
  python query_collection.py orders --where status=pending
  python query_collection.py orders --where status=pending --limit 5
"""

import argparse
import json
import os

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


def query_collection(collection, where=None, limit=None):
    """Query a Firestore collection."""
    args = {"collectionId": collection}

    if where:
        # Parse simple field=value into structured query
        # Format: field=value
        if "=" in where:
            field, value = where.split("=", 1)
            args["where"] = {
                "fieldFilter": {
                    "field": {"fieldPath": field},
                    "op": "EQUAL",
                    "value": {"stringValue": value},
                }
            }

    if limit:
        args["limit"] = limit

    return call_tool("firestore_query_collection", args)


def parse_firestore_value(value):
    """Convert Firestore typed value to Python native type."""
    if "stringValue" in value:
        return value["stringValue"]
    elif "integerValue" in value:
        return int(value["integerValue"])
    elif "doubleValue" in value:
        return value["doubleValue"]
    elif "booleanValue" in value:
        return value["booleanValue"]
    elif "nullValue" in value:
        return None
    elif "timestampValue" in value:
        return value["timestampValue"]
    elif "arrayValue" in value:
        return [parse_firestore_value(v) for v in value["arrayValue"].get("values", [])]
    elif "mapValue" in value:
        return {
            k: parse_firestore_value(v)
            for k, v in value["mapValue"].get("fields", {}).items()
        }
    elif "referenceValue" in value:
        return value["referenceValue"]
    elif "geoPointValue" in value:
        return value["geoPointValue"]
    elif "bytesValue" in value:
        return f"<bytes:{len(value['bytesValue'])}>"
    return value


def parse_document(doc):
    """Parse a Firestore document into readable format."""
    if "fields" in doc:
        return {k: parse_firestore_value(v) for k, v in doc["fields"].items()}
    return doc


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query a Firestore collection")
    parser.add_argument("collection", help="Collection ID to query")
    parser.add_argument("--where", help="Filter in format field=value")
    parser.add_argument("--limit", type=int, help="Maximum documents to return")

    args = parser.parse_args()

    try:
        query_desc = f"Querying collection: {args.collection}"
        if args.where:
            query_desc += f" (where {args.where})"
        if args.limit:
            query_desc += f" (limit {args.limit})"
        print(query_desc)
        print("=" * 50)

        result = query_collection(args.collection, args.where, args.limit)

        if "content" in result:
            for item in result["content"]:
                if item.get("type") == "text":
                    data = json.loads(item["text"])
                    if isinstance(data, list):
                        print(f"\nFound {len(data)} document(s):\n")
                        for doc in data:
                            if "name" in doc:
                                doc_path = doc["name"].split("/documents/")[-1]
                                print(f"📄 {doc_path}")
                                print("-" * 40)
                                parsed = parse_document(doc)
                                print(json.dumps(parsed, indent=2, default=str))
                                print()
                    elif "documents" in data:
                        docs = data["documents"]
                        print(f"\nFound {len(docs)} document(s):\n")
                        for doc in docs:
                            if "name" in doc:
                                doc_path = doc["name"].split("/documents/")[-1]
                                print(f"📄 {doc_path}")
                                print("-" * 40)
                                parsed = parse_document(doc)
                                print(json.dumps(parsed, indent=2, default=str))
                                print()
                    else:
                        print(json.dumps(data, indent=2))
        else:
            print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        print(f"\nUsing endpoint: {MCP_URL}")
