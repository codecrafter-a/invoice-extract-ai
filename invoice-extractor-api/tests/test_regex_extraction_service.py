from app.services.regex_extraction_service import RegexExtractionService

ENGLISH = """PACIFIC POWER & LIGHT
Utility Invoice

Invoice Date: March 15, 2025
Billing Period: 2025-02-01 to 2025-02-28
Service Address: 742 Evergreen Terrace, Springfield, IL 62704

Utility Type: Electricity
Energy Consumption: 847 kWh
"""

SPANISH = """GAS NATURAL DEL NORTE S.A.
Factura de Servicios

Fecha de Factura: 10 de marzo de 2025
Periodo de Facturacion: 01/02/2025 - 28/02/2025
Direccion de Servicio: Calle Mayor 45, Madrid

Tipo de Servicio: Gas
Consumo: 34.5 therms
"""


def test_english_extraction():
    result = RegexExtractionService().extract_invoice_data(ENGLISH)
    invoice = result["invoice"]
    assert invoice["invoice_date"] == "2025-03-15"
    assert invoice["utility_type"] == "electricity"
    assert invoice["usage_amount"] == 847.0
    assert invoice["usage_unit"].lower() == "kwh"
    assert invoice["billing_period_start"] == "2025-02-01"
    assert invoice["billing_period_end"] == "2025-02-28"
    assert result["detected_language"] == "en"


def test_spanish_extraction_and_language():
    result = RegexExtractionService().extract_invoice_data(SPANISH)
    invoice = result["invoice"]
    assert invoice["utility_type"] == "gas"
    assert invoice["usage_amount"] == 34.5
    assert invoice["billing_period_start"] == "2025-02-01"
    assert invoice["billing_period_end"] == "2025-02-28"
    assert result["detected_language"] == "es"


def test_confidence_is_zero_for_missing_fields():
    result = RegexExtractionService().extract_invoice_data("Just some unrelated text.")
    assert result["confidence"]["usage_amount"] == 0.0


def test_returns_all_field_keys():
    from app.constants.invoice_fields import FIELD_KEYS

    result = RegexExtractionService().extract_invoice_data(ENGLISH)
    assert set(result["invoice"].keys()) == set(FIELD_KEYS)
