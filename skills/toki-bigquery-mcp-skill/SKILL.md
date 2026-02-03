---
name: toki-bigquery
description: Execute BigQuery queries and export results for Toki's CRM database (toki-data-platform-prod). Use when you need to query BigQuery tables, analyze metering points, customers, contracts, invoices, pricing, or fetch metrics from the Toki CRM database. Handles Bulgarian terminology (точка, клиент, договор, фактура).
---

# Toki BigQuery MCP Skill

This skill connects to a local MCP server (Toolbox) that provides BigQuery access for the `toki-data-platform-prod.crm` dataset.

## Database Schema

**IMPORTANT**: Before writing queries, read `references/schema.md` for:
- Complete table schemas and relationships (29+ tables)
- Proven query patterns for point analysis, pricing, invoices
- Bulgarian ↔ English terminology mappings
- Critical business rules (Status values are CASE-SENSITIVE!)
- Full relationship map showing how tables connect

Key tables: point_agreements, metering_points, customers, contracts, invoices, prices, sbg_contracts

## Prerequisites

The MCP server must be running:
```bash
export BIGQUERY_PROJECT=toki-data-platform-prod
export BIGQUERY_LOCATION=EU
./toolbox --prebuilt bigquery --port 5001
```

Verify it's running:
```bash
curl http://127.0.0.1:5001/mcp/default
```

## Usage

### Query and Export BigQuery Data

Use the `scripts/mcp_query.py` script to execute SQL queries:

```bash
# Export as CSV (default)
python scripts/mcp_query.py "SELECT * FROM \`toki-data-platform-prod.crm.public_customers\` LIMIT 10"

# Export as JSON
python scripts/mcp_query.py "SELECT * FROM \`toki-data-platform-prod.crm.public_metering_points\` WHERE status='Active'" json

# Export as Parquet
python scripts/mcp_query.py "SELECT COUNT(*) as total FROM \`toki-data-platform-prod.crm.public_point_agreements\`" parquet
```

The tool returns:
- **download_url**: HTTP URL to download the exported file
- **filename**: Name of the exported file
- **row_count**: Number of rows in the result
- **file_size_bytes**: Size of the exported file
- **format**: Export format (csv/json/parquet)

### Available Tools

The MCP server exposes these tools:

**1. `export_bigquery_data`** (Primary tool)
- Executes SQL queries against BigQuery
- Exports results to a file (CSV/JSON/Parquet)
- Returns download URL for the results
- Arguments: `sql` (required), `format` (optional: csv/json/parquet)

**2. `list_bq_tables_sample`**
- Lists available BigQuery tables
- No arguments required

### List Available Tools

```bash
python scripts/list_tools.py
```

### List BigQuery Tables

```bash
python scripts/list_tables.py
```

## Examples

**Count active metering points:**
```bash
python scripts/mcp_query.py "SELECT COUNT(*) FROM \`toki-data-platform-prod.crm.public_point_agreements\` WHERE status='Active'"
```

**Get customers with contracts (JSON format):**
```bash
python scripts/mcp_query.py "SELECT c.name, co.contract_number FROM \`toki-data-platform-prod.crm.public_customers\` c JOIN \`toki-data-platform-prod.crm.public_contracts\` co ON c.customer_id = co.customer_id LIMIT 10" json
```

**Export invoice data (Parquet):**
```bash
python scripts/mcp_query.py "SELECT * FROM \`toki-data-platform-prod.crm.public_invoices\` WHERE billing_month >= '2024-01-01'" parquet
```

## Query Guidelines (from schema.md)

1. **ALWAYS use fully qualified table names** with backticks:
   ```sql
   `toki-data-platform-prod.crm.public_<table_name>`
   ```

2. **Status values are CASE-SENSITIVE**: Use 'Active' not 'active'

3. **NEVER add LIMIT unless explicitly requested** - users need complete data

4. **For period-based point analysis**: Start from `point_agreements` (the source of truth)

5. **Use the proven query patterns** from `references/schema.md`

## Troubleshooting

- **Connection refused**: Ensure MCP server is running on port 5001
- **MCP Error**: Check the Toolbox server logs for details
- **Empty results**: Verify table names (use `list_tables.py`) and check query syntax
- **Wrong status values**: Remember status is case-sensitive ('Active' not 'active')

## Configuration

- **MCP Endpoint**: `http://127.0.0.1:5001/mcp/default`
- **BigQuery Project**: `toki-data-platform-prod`
- **BigQuery Dataset**: `crm`
- **BigQuery Location**: `EU`
- **Table Prefix**: `public_`
