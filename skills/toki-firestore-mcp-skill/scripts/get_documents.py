#!/usr/bin/env python3
"""
Get Firestore documents by their paths.
Usage: python get_documents.py <path1> [path2] [path3] ...

Examples:
  python get_documents.py users/user123
  python get_documents.py users/user123 orders/order456
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


def get_documents(paths):
    """Get documents by their paths."""
    return call_tool("firestore_get_documents", {"paths": paths})


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
    if len(sys.argv) < 2:
        print("Usage: python get_documents.py <path1> [path2] ...")
        print("Example: python get_documents.py users/user123 orders/order456")
        sys.exit(1)

    paths = sys.argv[1:]

    try:
        print(f"Getting {len(paths)} document(s)...")
        print("=" * 50)

        result = get_documents(paths)

        if "content" in result:
            for item in result["content"]:
                if item.get("type") == "text":
                    data = json.loads(item["text"])
                    if isinstance(data, list):
                        for doc in data:
                            if "name" in doc:
                                # Extract document ID from full path
                                doc_path = doc["name"].split("/documents/")[-1]
                                print(f"\n📄 {doc_path}")
                                print("-" * 40)
                                parsed = parse_document(doc)
                                print(json.dumps(parsed, indent=2, default=str))
                    else:
                        print(json.dumps(data, indent=2))
        else:
            print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        print(f"\nUsing endpoint: {MCP_URL}")
