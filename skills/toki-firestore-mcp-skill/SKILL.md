---
name: toki-firestore
description: Access Firestore database for Toki. Query collections, get/add/update documents, list collections, and manage Firestore data. Use when you need to read or write Firestore documents, query collections with filters, or inspect database structure.
---

# Toki Firestore MCP Skill

This skill connects to a local MCP server (Toolbox) that provides Firestore access for Toki's Firestore database.

## Prerequisites

The MCP server must be running with the firestore toolset enabled:
```bash
export FIRESTORE_PROJECT=your-project-id
export FIRESTORE_DATABASE=  # optional, defaults to (default)
./toolbox --port 5001
```

Verify it's running:
```bash
curl -s -X POST http://127.0.0.1:5001/mcp/firestore \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

## Available Tools

### Document Operations
- `firestore_get_documents` - Get multiple documents by their paths
- `firestore_add_documents` - Add new documents to a collection
- `firestore_query_collection` - Query documents with filters

### Collection Operations
- `firestore_list_collections` - List collections under a parent path

### Commented Out (Available if Enabled)
- `firestore_update_document` - Update existing documents
- `firestore_delete_documents` - Delete documents by path
- `firestore_get_rules` - Get active security rules
- `firestore_validate_rules` - Validate rules syntax

## Usage Examples

### List Collections
```bash
python scripts/list_collections.py
```

### Get Documents
```bash
python scripts/get_documents.py "users/user123" "orders/order456"
```

### Query Collection
```bash
python scripts/query_collection.py "users" --where "status=active"
```

### Add Document
```bash
python scripts/add_document.py "users" '{"name": "John", "email": "john@example.com"}'
```

## Document Data Format

Firestore uses typed values. When adding or updating documents, use the proper type wrappers:

```json
{
  "fields": {
    "name": {"stringValue": "John Doe"},
    "age": {"integerValue": "30"},
    "active": {"booleanValue": true},
    "balance": {"doubleValue": 100.50},
    "createdAt": {"timestampValue": "2024-01-15T10:30:00Z"},
    "tags": {
      "arrayValue": {
        "values": [
          {"stringValue": "premium"},
          {"stringValue": "verified"}
        ]
      }
    },
    "metadata": {
      "mapValue": {
        "fields": {
          "source": {"stringValue": "web"},
          "version": {"integerValue": "2"}
        }
      }
    }
  }
}
```

### Type Reference

| Firestore Type | JSON Format |
|---------------|-------------|
| String | `{"stringValue": "text"}` |
| Integer | `{"integerValue": "123"}` |
| Double | `{"doubleValue": 123.45}` |
| Boolean | `{"booleanValue": true}` |
| Timestamp | `{"timestampValue": "RFC3339"}` |
| Null | `{"nullValue": null}` |
| Bytes | `{"bytesValue": "base64data"}` |
| Reference | `{"referenceValue": "projects/.../documents/..."}` |
| GeoPoint | `{"geoPointValue": {"latitude": 0, "longitude": 0}}` |
| Array | `{"arrayValue": {"values": [...]}}` |
| Map | `{"mapValue": {"fields": {...}}}` |

## Query Operators

When querying collections, these filter operators are supported:

| Operator | Description |
|----------|-------------|
| `EQUAL` | Field equals value |
| `NOT_EQUAL` | Field does not equal value |
| `LESS_THAN` | Field is less than value |
| `LESS_THAN_OR_EQUAL` | Field is less than or equal |
| `GREATER_THAN` | Field is greater than value |
| `GREATER_THAN_OR_EQUAL` | Field is greater than or equal |
| `ARRAY_CONTAINS` | Array field contains value |
| `ARRAY_CONTAINS_ANY` | Array contains any of values |
| `IN` | Field is in list of values |
| `NOT_IN` | Field is not in list of values |

## Best Practices

1. **Use Typed Values**: Always wrap field values with type indicators
2. **Use updateMask for Precision**: When updating, specify only fields to change
3. **Avoid returnData Unless Needed**: Only set `returnData: true` when verification is required
4. **Use RFC3339 for Timestamps**: e.g., `2024-01-15T10:30:00Z`
5. **Base64 Encode Binary Data**: For `bytesValue` fields

## Troubleshooting

### Connection Refused
- Ensure MCP server is running: `curl http://127.0.0.1:5001/mcp/firestore`
- Check that the firestore toolset is enabled in your config

### Authentication Error
- Verify FIRESTORE_PROJECT environment variable is set
- Ensure you have proper Google Cloud credentials configured

### Permission Denied
- Check Firestore security rules
- Verify service account has required IAM permissions

### Document Not Found
- Verify document path is correct (collection/docId format)
- Check if document exists in Firestore console

### Invalid Document Data
- Ensure all fields use typed value wrappers
- Verify timestamp format is RFC3339
- Check that integer values are strings in JSON

## Configuration

- **MCP Endpoint**: `http://127.0.0.1:5001/mcp/firestore`
- **Firestore Project**: `${FIRESTORE_PROJECT}`
- **Firestore Database**: `${FIRESTORE_DATABASE}` (defaults to `(default)`)
