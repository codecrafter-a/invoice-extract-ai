import csv

from app.constants.invoice_fields import CSV_HEADERS, FIELD_KEYS, INVOICE_FIELDS
from app.services.csv_service import CsvService


def test_ssot_includes_billing_period_fields():
    assert "billing_period_start" in FIELD_KEYS
    assert "billing_period_end" in FIELD_KEYS


def test_ssot_has_all_required_spec_fields():
    required = {
        "vendor_name",
        "invoice_date",
        "service_address",
        "utility_type",
        "usage_amount",
        "usage_unit",
        "billing_period_start",
        "billing_period_end",
    }
    assert required.issubset(set(FIELD_KEYS))


def test_headers_and_keys_align():
    assert len(CSV_HEADERS) == len(FIELD_KEYS) == len(INVOICE_FIELDS)


def test_csv_generation_round_trip():
    invoice = {key: None for key in FIELD_KEYS} | {
        "vendor_name": "Acme Power",
        "utility_type": "electricity",
        "usage_amount": 100.0,
        "billing_period_start": "2025-02-01",
        "billing_period_end": "2025-02-28",
    }
    csv_id, path = CsvService().generate_csv(invoice)
    try:
        with path.open(encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        assert rows[0] == CSV_HEADERS
        row = rows[1]
        assert "Acme Power" in row
        assert "2025-02-28" in row
    finally:
        path.unlink(missing_ok=True)
