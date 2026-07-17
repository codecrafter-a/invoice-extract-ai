"""Unit tests for OpenAIService response normalization (no network calls)."""

import os

import pytest

from app.constants.invoice_fields import FIELD_KEYS


@pytest.fixture
def service(monkeypatch):
    # Provide a fake key so __init__ doesn't raise; we never make a real call.
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-real")
    from app.services.openai_service import OpenAIService

    return OpenAIService()


def test_normalize_nested_invoice(service):
    parsed = {
        "invoice": {key: None for key in FIELD_KEYS}
        | {"vendor_name": "Acme", "usage_amount": "1,234.5", "utility_type": "electricity"},
        "detected_language": "EN",
        "confidence": {"vendor_name": 1.5, "usage_amount": 0.9},
    }
    result = service._normalize_response(parsed)
    assert result["invoice"]["vendor_name"] == "Acme"
    assert result["invoice"]["usage_amount"] == 1234.5  # comma stripped, float
    assert result["detected_language"] == "en"  # lowercased
    assert result["confidence"]["vendor_name"] == 1.0  # clamped to 1.0
    assert result["confidence"]["usage_amount"] == 0.9


def test_normalize_flat_invoice(service):
    parsed = {key: None for key in FIELD_KEYS} | {"vendor_name": "Flat Co"}
    result = service._normalize_response(parsed)
    assert result["invoice"]["vendor_name"] == "Flat Co"
    assert result["detected_language"] is None
    assert result["confidence"] == {}


def test_normalize_bad_usage_amount_becomes_none(service):
    parsed = {"invoice": {"usage_amount": "not-a-number"}}
    result = service._normalize_response(parsed)
    assert result["invoice"]["usage_amount"] is None
