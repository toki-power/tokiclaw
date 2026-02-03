# Toki Looker MCP Tools Guide

This guide documents all available Looker tools via the MCP server.

## CONNECTION INFO
- MCP Endpoint: `http://127.0.0.1:5001/mcp/looker`
- Toolset: `looker`
- Authentication: OAuth via LOOKER_CLIENT_ID and LOOKER_CLIENT_SECRET

## IMPORTANT: KNOWN LIMITATIONS

**Looker explores may return empty results** even with valid queries. Common causes:

1. **Required filters** - Many explores require date range or other mandatory filters
2. **Permission restrictions** - API credentials may have limited data access
3. **Data availability** - Some explores are for visualization only; raw data lives in BigQuery

**Recommended approach:**
- Use `looker_get_looks` and `looker_run_look` to run pre-built saved looks (more reliable)
- Use `looker_query_url` to generate URLs and debug queries in Looker UI
- For raw data access, **prefer BigQuery** via the `toki-bigquery` skill

**When Looker returns empty:**
1. Check if the explore has required filters (use `looker_get_filters`)
2. Try running a saved look instead of ad-hoc query
3. Fall back to BigQuery for direct table access

## TOOL REFERENCE

### Discovery Tools

#### looker_get_models
List all LookML models in the Looker instance.

**Parameters:** None

**Example:**
```bash
curl -s -X POST http://127.0.0.1:5001/mcp/looker \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"looker_get_models","arguments":{}}}'
```

**Returns:** Array of model objects with `name`, `label`, `explores`

---

#### looker_get_explores
List explores in a LookML model.

**Parameters:**
- `model_name` (required) - Name of the LookML model

**Example:**
```bash
curl -s -X POST http://127.0.0.1:5001/mcp/looker \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"looker_get_explores","arguments":{"model_name":"toki_crm"}}}'
```

**Returns:** Array of explore objects with `name`, `label`, `description`

---

#### looker_get_dimensions
List dimensions in an explore.

**Parameters:**
- `model_name` (required) - Name of the LookML model
- `explore_name` (required) - Name of the explore

**Example:**
```bash
curl -s -X POST http://127.0.0.1:5001/mcp/looker \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"looker_get_dimensions","arguments":{"model_name":"toki_crm","explore_name":"customers"}}}'
```

**Returns:** Array of dimension objects with `name`, `label`, `type`, `sql`

---

#### looker_get_measures
List measures in an explore.

**Parameters:**
- `model_name` (required) - Name of the LookML model
- `explore_name` (required) - Name of the explore

**Returns:** Array of measure objects with `name`, `label`, `type`, `sql`

---

#### looker_get_filters
List filters in an explore.

**Parameters:**
- `model_name` (required) - Name of the LookML model
- `explore_name` (required) - Name of the explore

**Returns:** Array of filter objects

---

#### looker_get_parameters
List parameters in an explore.

**Parameters:**
- `model_name` (required) - Name of the LookML model
- `explore_name` (required) - Name of the explore

**Returns:** Array of parameter objects

---

### Query Tools

#### looker_query
Run a query against a LookML model.

**Parameters:**
- `model_id` (required) - Name of the LookML model
- `explore_name` (required) - Name of the explore
- `fields` (required) - Array of field names to select
- `filters` (optional) - Object of field:value filters
- `sorts` (optional) - Array of sort fields (prefix with `-` for descending)
- `pivots` (optional) - Array of pivot fields
- `row_limit` (optional) - Maximum rows to return
- `query_timezone` (optional) - Timezone for query

**Example:**
```bash
curl -s -X POST http://127.0.0.1:5001/mcp/looker \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":1,
    "method":"tools/call",
    "params":{
      "name":"looker_query",
      "arguments":{
        "model_id":"toki_crm",
        "explore_name":"customers",
        "fields":["customer.name","customer.status","customer.count"],
        "filters":{"customer.status":"Active"},
        "row_limit":100
      }
    }
  }'
```

**Returns:** Query results as array of objects

---

#### looker_query_sql
Generate the SQL Looker would run for a query.

**Parameters:** Same as `looker_query`

**Returns:** SQL string

---

#### looker_query_url
Generate a Looker URL for a query (can be opened in browser).

**Parameters:** 
- Same as `looker_query`
- `vis_config` (optional) - Visualization configuration object

**Returns:** Looker URL string

---

### Look Management

#### looker_get_looks
Search for saved looks.

**Parameters:**
- `title` (optional) - Search by title
- `limit` (optional) - Max results (default 50)
- `offset` (optional) - Pagination offset

**Example:**
```bash
curl -s -X POST http://127.0.0.1:5001/mcp/looker \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"looker_get_looks","arguments":{"title":"revenue","limit":10}}}'
```

**Returns:** Array of look objects with `id`, `title`, `folder`

---

#### looker_run_look
Run a saved look and return data.

**Parameters:**
- `look_id` (required) - ID of the look to run

**Returns:** Query results as array of objects

---

#### looker_make_look
Create a new look from query parameters.

**Parameters:**
- `title` (required) - Look title
- `description` (optional) - Look description
- `model_id` (required) - LookML model name
- `explore_name` (required) - Explore name
- `fields` (required) - Array of field names
- `filters` (optional) - Filter object
- `vis_config` (optional) - Visualization config

**Returns:** Created look object with `id`

---

### Dashboard Management

#### looker_get_dashboards
Search for saved dashboards.

**Parameters:**
- `title` (optional) - Search by title
- `limit` (optional) - Max results
- `offset` (optional) - Pagination offset

**Returns:** Array of dashboard objects with `id`, `title`, `folder`

---

#### looker_make_dashboard
Create a new empty dashboard.

**Parameters:**
- `title` (required) - Dashboard title
- `description` (optional) - Dashboard description

**Returns:** Created dashboard object with `id`

---

#### looker_add_dashboard_element
Add a tile to a dashboard.

**Parameters:**
- `dashboard_id` (required) - ID of the dashboard
- `title` (optional) - Tile title
- `model_id` (required) - LookML model name
- `explore_name` (required) - Explore name
- `fields` (required) - Array of field names
- `filters` (optional) - Filter object
- `vis_config` (optional) - Visualization configuration

**Returns:** Created element object

---

## COMMON WORKFLOWS

### 1. Discover Available Data
```
1. looker_get_models → List all models
2. looker_get_explores → List explores in a model
3. looker_get_dimensions + looker_get_measures → See available fields
```

### 2. Run Ad-hoc Query
```
1. looker_query → Run query with fields and filters
   OR
2. looker_query_sql → Get SQL to review
3. looker_query_url → Get URL to open in Looker
```

### 3. Work with Saved Content
```
1. looker_get_looks → Find saved looks
2. looker_run_look → Run a look by ID
```

### 4. Create Dashboard
```
1. looker_make_dashboard → Create empty dashboard
2. looker_add_dashboard_element → Add tiles to dashboard
```

---

## FIELD NAMING CONVENTIONS

Fields in Looker follow the pattern: `view_name.field_name`

Examples:
- `customer.name` - Customer name dimension
- `customer.status` - Customer status dimension
- `customer.count` - Customer count measure
- `order.total_amount` - Order total measure
- `order.created_date` - Order date dimension

---

## FILTER SYNTAX

Filters are passed as objects with field:value pairs:

```json
{
  "customer.status": "Active",
  "order.created_date": "30 days",
  "customer.name": "%Toki%"
}
```

Common filter expressions:
- Exact match: `"Active"`
- Contains: `"%search%"`
- Not equal: `"-Inactive"`
- Multiple values: `"Active,Pending"`
- Numeric range: `">=100"`
- Date range: `"2024-01-01 to 2024-12-31"`
- Relative date: `"30 days"`, `"this month"`, `"last quarter"`

---

## SORT SYNTAX

Sorts are passed as an array of field names:
- Ascending: `["customer.name"]`
- Descending: `["-customer.name"]` (prefix with `-`)
- Multiple: `["customer.status", "-customer.count"]`

---

## VIS_CONFIG EXAMPLES

### Table
```json
{
  "type": "looker_grid"
}
```

### Bar Chart
```json
{
  "type": "looker_bar",
  "show_value_labels": true
}
```

### Line Chart
```json
{
  "type": "looker_line",
  "show_null_points": false
}
```

### Pie Chart
```json
{
  "type": "looker_pie"
}
```

### Single Value
```json
{
  "type": "single_value",
  "show_comparison": false
}
```

---

## ERROR HANDLING

Common errors:
- **"Model not found"** - Check model name with `looker_get_models`
- **"Explore not found"** - Check explore name with `looker_get_explores`
- **"Field not found"** - Check field names with `looker_get_dimensions`/`looker_get_measures`
- **"Authentication failed"** - Verify LOOKER_CLIENT_ID and LOOKER_CLIENT_SECRET
- **"Timeout"** - Query may be too complex; try adding filters or reducing row_limit

---

## BULGARIAN TERMINOLOGY (Toki-specific)

- клиент = customer
- договор = contract
- точка = metering point
- фактура = invoice
- план = plan
- консумация = consumption
- активен = Active
- неактивен = Inactive
