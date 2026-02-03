---
name: toki-looker
description: Connect to Looker MCP server to explore LookML models, run queries, create looks and dashboards. Use when you need to analyze data via Looker, generate visualizations, or manage Looker content.
---

# Toki Looker MCP Skill

This skill connects to a local MCP server that provides Looker API access via JSON-RPC transport.

## Setup

The MCP server should be running at: `http://127.0.0.1:5001/mcp/looker`

Verify it's running:
```bash
curl -s -X POST http://127.0.0.1:5001/mcp/looker \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

## Available Tools

### Discovery Tools
- `looker_get_models` - List LookML models in the Looker instance
- `looker_get_explores` - List explores in a model (requires model_name)
- `looker_get_dimensions` - List dimensions in an explore
- `looker_get_measures` - List measures in an explore
- `looker_get_filters` - List filters in an explore
- `looker_get_parameters` - List parameters in an explore

### Query Tools
- `looker_query` - Run a query against a LookML model
- `looker_query_sql` - Generate the SQL Looker would run for a query
- `looker_query_url` - Generate a Looker URL for a query

### Look Management
- `looker_get_looks` - Search saved looks
- `looker_run_look` - Run a look and return data
- `looker_make_look` - Create a new look from query params

### Dashboard Management
- `looker_get_dashboards` - Search saved dashboards
- `looker_make_dashboard` - Create a new empty dashboard
- `looker_add_dashboard_element` - Add a tile to a dashboard

## Usage Examples

### List Models
```bash
python scripts/looker_models.py
```

### Explore a Model
```bash
python scripts/looker_explore.py model_name explore_name
```

### Run a Query
```bash
python scripts/looker_query.py model_name explore_name "field1,field2" --filters '{"field":"value"}'
```

## Important Notes

### Query Requirements

**⚠️ CRITICAL**: Looker explore queries **must include at least one measure** (not just dimensions).

**Common Error:**
```
"Must query at least one dimension or measure"
```

**Solution:** Always include at least one measure field in your query:
```json
{
  "fields": [
    "explore.dimension_field",     // ✓ Dimension
    "explore.measure_field"         // ✓ Measure (REQUIRED!)
  ]
}
```

### Best Practices

1. **Use Saved Looks When Available** - Looks are pre-configured and more reliable than direct explore queries
2. **Always Query with Measures** - Include at least one aggregation/measure field
3. **Check for Empty Results** - Some explores may return empty results without specific filters
4. **Start with Dimensions Discovery** - Use `looker_get_dimensions` and `looker_get_measures` to discover available fields

### Data Access Methods (Ordered by Reliability)

1. ✅ **Saved Looks** (`looker_run_look`) - Most reliable, pre-configured
2. ✅ **Direct Queries with Measures** (`looker_query`) - Works if you include measures
3. ⚠️ **Direct Queries (dimension-only)** - Will fail with error
4. ⚠️ **Explores without Filters** - May return empty results

## Known Working Examples

### Models and Explores (Verified Working)

**Financial Planning**
- Model: `financial_planning`
- Looks: `Financial Planning` (ID: 1), `Financial Planning Next` (ID: 2)
- Fields: customer_name, metering_point_id, measurement_mwh, markup_percent, etc.

**Protocols**
- Model: `protocols`
- Explore: `filtered_protocols`
- Dimensions: point_id, customer details
- Measures: count, total_cost_sum (required for queries!)

**Metering Data**
- Model: `metering_data_v1`
- Explore: `billing_measurement_latest_v1`
- Dimensions: timestamp_date, timestamp_hour, point_id
- Measures: total_measurement, total_hourly_cost (required!)

### Example: Running a Saved Look

```bash
# List available looks
curl -X POST http://127.0.0.1:5001/mcp/looker \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":1,
    "method":"tools/call",
    "params":{
      "name":"looker_get_looks",
      "arguments":{}
    }
  }'

# Run a look
curl -X POST http://127.0.0.1:5001/mcp/looker \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":1,
    "method":"tools/call",
    "params":{
      "name":"looker_run_look",
      "arguments":{
        "look_id":"1",
        "limit":50
      }
    }
  }'
```

### Example: Direct Query with Measures

```bash
# ✓ CORRECT - Includes measures
curl -X POST http://127.0.0.1:5001/mcp/looker \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":1,
    "method":"tools/call",
    "params":{
      "name":"looker_query",
      "arguments":{
        "model":"protocols",
        "explore":"filtered_protocols",
        "fields":[
          "filtered_protocols.point_id",
          "filtered_protocols.count"
        ],
        "limit":20
      }
    }
  }'

# ✗ WRONG - Only dimensions (will fail!)
curl -X POST http://127.0.0.1:5001/mcp/looker \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":1,
    "method":"tools/call",
    "params":{
      "name":"looker_query",
      "arguments":{
        "model":"protocols",
        "explore":"filtered_protocols",
        "fields":["filtered_protocols.point_id"],
        "limit":20
      }
    }
  }'
```

## Troubleshooting

### "Must query at least one dimension or measure"
- **Cause**: Query includes only dimensions, no measures
- **Solution**: Add at least one measure field (e.g., count, sum, average)
- **Example**: Add `explore.count` or `explore.total_measurement` to your fields

### Empty Results from Explores
- **Cause**: Explore may require specific filters or has no data
- **Solution**: 
  1. Try using a saved Look instead
  2. Add date filters (e.g., `"timestamp_date":"7 days ago for 7 days"`)
  3. Check if the explore has data in Looker UI first

### Connection Refused
- **Cause**: MCP server not running
- **Solution**: Ensure MCP server is running on port 5001 with looker toolset

### Authentication Error
- **Cause**: Missing or invalid Looker credentials
- **Solution**: Check LOOKER_CLIENT_ID and LOOKER_CLIENT_SECRET env vars

### Tool Not Found
- **Cause**: Requested tool doesn't exist
- **Solution**: Run `python scripts/list_tools.py` to see available tools
