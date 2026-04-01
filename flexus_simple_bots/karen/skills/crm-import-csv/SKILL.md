---
name: crm-import-csv
description: Walk the user through bulk-importing records from a CSV file — field mapping, normalization script, and erp_csv_import.
---

# Bulk Importing Records from CSV

When a user wants to import records (e.g., contacts) from a CSV, follow this process:

## Step 1: Get the CSV File

Ask the user to upload their CSV file. They can attach it to the chat, and you will access it via mongo_store.

## Step 2: Analyze CSV and Target Table

1. Read the CSV (headers + sample rows) from Mongo
2. Call erp_table_meta() to retrieve the full schema of the target table (e.g., crm_contact)
3. Identify standard fields and the JSON details field for custom data

## Step 3: Propose Field Mapping

Create an intelligent mapping from CSV to table fields:

1. Match columns by name similarity
2. Propose transformations where needed (e.g., split full name, normalize phone/email, parse dates)
3. Map unmatched CSV columns into the appropriate *_details JSON field
4. Suggest an upsert key for deduplication (e.g., contact_email) if possible

Present the mapping to the user in a clear format:
```
CSV Column -> Target Field (Transformation)
-----------------------------------------
Email -> contact_email (lowercase, trim)
Full Name -> contact_first_name + contact_last_name (split on first space)
Phone -> contact_phone (format: remove non-digits)
Company -> contact_details.company (custom field)
Source -> contact_details.source (custom field)

Upsert key: contact_email (will update existing contacts with same email)
```

## Step 4: Validate and Adjust

Ask the user to confirm or modify, field mappings, transformations, upsert behavior, validation rules

## Step 5: Generate Python Script to Normalize the CSV

Use python_execute() only to transform the uploaded file into a clean CSV whose columns exactly match the ERP table. Read from the Mongo attachment and write a new CSV:

```python
import pandas as pd

SOURCE_FILE = "attachments/solar_root/leads_rows.csv"
TARGET_TABLE = "crm_contact"
OUTPUT_FILE = f"{TARGET_TABLE}_import.csv"

df = pd.read_csv(SOURCE_FILE)
records = []
for _, row in df.iterrows():
    full_name = str(row.get("Full Name", "")).strip()
    parts = full_name.split(" ", 1)
    first_name = parts[0] if parts else ""
    last_name = parts[1] if len(parts) > 1 else ""
    record = {
        "contact_first_name": first_name,
        "contact_last_name": last_name,
        "contact_email": str(row.get("Email", "")).strip().lower(),
        "contact_phone": str(row.get("Phone", "")).strip(),
        "contact_details": {
            "company": str(row.get("Company", "")).strip(),
            "source": "csv_import"
        }
    }
    records.append(record)

normalized = pd.DataFrame(records)
normalized.to_csv(OUTPUT_FILE, index=False)
print(f"Saved {OUTPUT_FILE} with {len(normalized)} rows")
```

python_execute automatically uploads generated files back to Mongo under their filenames (e.g., `crm_contact_import.csv`), so you can reference them with mongo_store or the new import tool.

## Step 6: Review the Normalized File

1. Use `mongo_store(op="cat", args={"path": "crm_contact_import.csv"})` to show the first rows
2. Confirm every column matches the ERP schema (no extras, correct casing) and the upsert key looks good
3. Share stats (row count, notable transforms) with the user

## Step 7: Import with `erp_csv_import`

Use erp_csv_import() to import the cleaned CSV.

After import, offer to create follow-up tasks or automations for the new contacts.
