# Load Profile Export Format

This document defines the expected format for load profile (товаров профил) exports.

## What is a Load Profile?

A load profile shows **interval-level electricity consumption** - typically 15-minute or hourly measurements from smart meters.

**This is different from billing data**, which contains monthly aggregated totals.

## Data Source

- **NOT available** in the CRM database (`meter_readings`, `invoices` have only monthly sums)
- Typically sourced from:
  - ERP system raw exports (from distribution companies like ЕРМ Запад)
  - SCADA systems
  - Smart meter data aggregation platforms
  - Separate `load_profile` or `interval_readings` table (if it exists in BigQuery)

## Expected Format: Wide Table (Pivot)

### Structure

```
Timestamp         Minute15  Price  32Z103002177393I  32Z103002183349Z  32Z103002183350D  ...
2025-05-01 00:00  194.84    2.25   0.27              0.12              0.50              ...
2025-05-01 00:15            2.50   0.26              0.12              0.50              ...
2025-05-01 00:30            3.00   0.25              0.11              0.50              ...
2025-05-01 00:45            3.25   0.26              0.12              0.50              ...
2025-05-01 01:00  194.86    3.00   0.25              0.11              0.50              ...
```

### Column Definitions

| Column | Type | Description |
|--------|------|-------------|
| `Timestamp` | DATETIME | Start of the interval (e.g., "2025-05-01 00:00") |
| `Minute15` | FLOAT | Cumulative or interval marker (optional, varies by export) |
| `Price` | FLOAT | Day-ahead market price for that interval (лв/MWh) |
| `32Z103002177393I` | FLOAT | kWh consumed by this metering point (ITN) in the interval |
| `32Z103002183349Z` | FLOAT | kWh consumed by another metering point |
| ... | ... | One column per metering point |

### Key Characteristics

- **Rows**: One per time interval (15-min or hourly)
- **Columns**: One per metering point (ITN number)
- **Values**: kWh consumed during that specific interval
- **Interval frequency**: Typically 15 minutes (96 rows per day) or 1 hour (24 rows per day)

## Example Use Case

**User request**: "Дай ми товаров профил за ФЕРИЯ 2000 ООД за 2025 година"

**What they want**: 15-minute interval data showing consumption for each hour/quarter-hour throughout 2025.

**What CRM has**: Only monthly totals like "May 2025: 3,130 kWh (day zone), 2,844 kWh (night zone)"

**Solution**: 
1. Check if a `public_load_profile` table exists in BigQuery
2. If not, ask user to provide ERP export URL or CSV file with 15-minute data
3. Transform long format (if needed) into wide format using SQL pivot or Python

## Conversion: Long to Wide Format

If data arrives in **long format**:

```
timestamp           | metering_point_id    | kwh
2025-05-01 00:00   | 32Z103002177393I     | 0.27
2025-05-01 00:00   | 32Z103002183349Z     | 0.12
2025-05-01 00:15   | 32Z103002177393I     | 0.26
```

Use a **PIVOT** query to convert to wide format:

```sql
SELECT
  timestamp,
  MAX(IF(metering_point_id = '32Z103002177393I', kwh, NULL)) AS `32Z103002177393I`,
  MAX(IF(metering_point_id = '32Z103002183349Z', kwh, NULL)) AS `32Z103002183349Z`,
  -- ... repeat for each metering point
FROM load_profile_raw
GROUP BY timestamp
ORDER BY timestamp
```

## Common Pitfalls

### ❌ Wrong: Providing Monthly Aggregated Data

```csv
metering_point_id,reading_end_date,tariff_type,kwh
32Z103002177393I,2025-05-31,"Дневна зона",3130
32Z103002177393I,2025-05-31,"Нощна зона",2844
```

This is **invoice-level data** - useful for billing, not for load profiling.

### ✅ Correct: Providing Interval Data

```csv
timestamp,32Z103002177393I,32Z103002183349Z
2025-05-01 00:00,0.27,0.12
2025-05-01 00:15,0.26,0.12
2025-05-01 00:30,0.25,0.11
```

This shows **actual consumption per interval** - suitable for load analysis.

## Bulgarian Terminology

| English | Bulgarian |
|---------|-----------|
| Load profile | Товаров профил |
| Interval | Интервал |
| 15-minute interval | 15-минутен интервал |
| Hourly profile | Почасов профил |
| Metering point | Точка на измерване |
| Consumption | Консумация / Потребление |
| Day zone | Дневна зона |
| Night zone | Нощна зона |

## Next Steps if Load Profile Data is Unavailable

1. **Check for existing tables**:
   ```sql
   SELECT table_id 
   FROM `toki-data-platform-prod.crm.__TABLES__` 
   WHERE table_id LIKE '%load%' OR table_id LIKE '%interval%'
   ```

2. **Ask user for source**:
   - "Имате ли експорт от ЕРП системата с 15-минутни данни?"
   - "Може ли да споделите CSV файл с почасови измервания?"

3. **Suggest alternative**:
   - Use monthly aggregated data for high-level analysis
   - Contact ERP provider (ЕРМ Запад, EVN, etc.) for interval exports
