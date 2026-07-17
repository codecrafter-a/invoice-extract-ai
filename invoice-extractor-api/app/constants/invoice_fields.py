INVOICE_FIELDS = [
    # Primary (key) fields — always shown in the results summary table.
    {
        "key": "vendor_name",
        "label": "Vendor Name",
        "type": "string",
        "required": True,
        "primary": True,
    },
    {
        "key": "invoice_date",
        "label": "Invoice Date",
        "type": "date",
        "required": True,
        "primary": True,
    },
    {
        "key": "utility_type",
        "label": "Utility Type",
        "type": "enum",
        "required": True,
        "allowed": ["electricity", "gas", "water"],
        "primary": True,
    },
    {
        "key": "usage_amount",
        "label": "Usage Amount",
        "type": "number",
        "required": True,
        "primary": True,
    },
    {
        "key": "usage_unit",
        "label": "Usage Unit",
        "type": "string",
        "required": True,
        "primary": True,
    },
    {
        "key": "total_amount",
        "label": "Total Amount Due",
        "type": "number",
        "required": False,
        "primary": True,
    },
    {
        "key": "billing_period_start",
        "label": "Billing Period Start",
        "type": "date",
        "required": False,
        "primary": True,
    },
    {
        "key": "billing_period_end",
        "label": "Billing Period End",
        "type": "date",
        "required": False,
        "primary": True,
    },
    # Additional details — shown under the "View details" section in the UI.
    {
        "key": "service_address",
        "label": "Service Address",
        "type": "string",
        "required": False,
        "primary": False,
    },
    {
        "key": "invoice_number",
        "label": "Invoice Number",
        "type": "string",
        "required": False,
        "primary": False,
    },
    {
        "key": "account_number",
        "label": "Account Number",
        "type": "string",
        "required": False,
        "primary": False,
    },
    {
        "key": "due_date",
        "label": "Due Date",
        "type": "date",
        "required": False,
        "primary": False,
    },
    {
        "key": "currency",
        "label": "Currency",
        "type": "string",
        "required": False,
        "primary": False,
    },
    {
        "key": "tax_amount",
        "label": "Tax Amount",
        "type": "number",
        "required": False,
        "primary": False,
    },
    {
        "key": "meter_number",
        "label": "Meter Number",
        "type": "string",
        "required": False,
        "primary": False,
    },
]

FIELD_KEYS = [field["key"] for field in INVOICE_FIELDS]
CSV_HEADERS = [field["label"] for field in INVOICE_FIELDS]
