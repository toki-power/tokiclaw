#!/usr/bin/env python3
"""
Add a document to a Firestore collection.
Usage: python add_document.py <collection> <json_data> [--id doc_id]

Examples:
  python add_document.py users '{"name": "John", "email": "john@example.com"}'
  python add_document.py users '{"name": "John"}' --id user123
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


def python_to_firestore(value):
    """Convert Python value to Firestore typed value."""
    if value is None:
        return {"nullValue": None}
    elif isinstance(value, bool):
        return {"booleanValue": value}
    elif isinstance(value, int):
        return {"integerValue": str(value)}
    elif isinstance(value, float):
        return {"doubleValue": value}
    elif isinstance(value, str):
        return {"stringValue": value}
    elif isinstance(value, list):
        return {"arrayValue": {"values": [python_to_firestore(v) for v in value]}}
    elif isinstance(value, dict):
        return {
            "mapValue": {
                "fields": {k: python_to_firestore(v) for k, v in value.items()}
            }
        }
    else:
        return {"stringValue": str(value)}


def add_document(collection, data, doc_id=None):
    """Add a document to a Firestore collection."""
    # Convert simple dict to Firestore format
    fields = {k: python_to_firestore(v) for k, v in data.items()}

    document = {"collectionId": collection, "documentData": {"fields": fields}}

    if doc_id:
        document["documentId"] = doc_id

    return call_tool("firestore_add_documents", {"documents": [document]})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a document to Firestore")
    parser.add_argument("collection", help="Collection ID")
    parser.add_argument("data", help="JSON data for the document")
    parser.add_argument("--id", dest="doc_id", help="Optional document ID")

    args = parser.parse_args()

    try:
        data = json.loads(args.data)

        print(f"Adding document to collection: {args.collection}")
        if args.doc_id:
            print(f"Document ID: {args.doc_id}")
        print("=" * 50)
        print(f"Data: {json.dumps(data, indent=2)}")
        print()

        result = add_document(args.collection, data, args.doc_id)

        if "content" in result:
            for item in result["content"]:
                if item.get("type") == "text":
                    response = json.loads(item["text"])
                    print("✅ Document created successfully!")
                    if isinstance(response, list) and len(response) > 0:
                        doc = response[0]
                        if "name" in doc:
                            doc_path = doc["name"].split("/documents/")[-1]
                            print(f"Path: {doc_path}")
                    else:
                        print(json.dumps(response, indent=2))
        else:
            print(json.dumps(result, indent=2))

    except json.JSONDecodeError as e:
        print(f"Invalid JSON data: {e}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"\nUsing endpoint: {MCP_URL}")
