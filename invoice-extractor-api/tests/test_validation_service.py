from app.services.validation_service import ValidationService


def make_invoice(**overrides):
    base = {
        "vendor_name": "Acme Power",
        "invoice_date": "2025-03-15",
        "service_address": "1 Main St",
        "utility_type": "electricity",
        "usage_amount": 100.0,
        "usage_unit": "kWh",
        "billing_period_start": "2025-02-01",
        "billing_period_end": "2025-02-28",
    }
    base.update(overrides)
    return base


def test_valid_invoice_has_no_warnings():
    _, warnings = ValidationService().validate(make_invoice())
    assert warnings == []


def test_missing_required_field_warns():
    _, warnings = ValidationService().validate(make_invoice(vendor_name=None))
    assert any(w.field == "vendor_name" for w in warnings)


def test_missing_optional_field_is_ok():
    _, warnings = ValidationService().validate(
        make_invoice(billing_period_start=None, billing_period_end=None)
    )
    assert warnings == []


def test_invalid_date_format_warns_and_nulls():
    validated, warnings = ValidationService().validate(make_invoice(invoice_date="15/03/2025"))
    assert validated["invoice_date"] is None
    assert any(w.field == "invoice_date" for w in warnings)


def test_negative_usage_warns():
    _, warnings = ValidationService().validate(make_invoice(usage_amount=-5))
    assert any(w.field == "usage_amount" for w in warnings)


def test_invalid_utility_type_warns():
    _, warnings = ValidationService().validate(make_invoice(utility_type="solar"))
    assert any(w.field == "utility_type" for w in warnings)


def test_utility_type_is_lowercased():
    validated, _ = ValidationService().validate(make_invoice(utility_type="Electricity"))
    assert validated["utility_type"] == "electricity"


def test_billing_period_reversed_warns():
    _, warnings = ValidationService().validate(
        make_invoice(billing_period_start="2025-02-28", billing_period_end="2025-02-01")
    )
    assert any(w.field == "billing_period_end" for w in warnings)
