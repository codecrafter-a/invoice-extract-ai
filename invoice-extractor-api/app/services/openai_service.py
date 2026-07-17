import json
import os
from typing import Any

from openai import APIConnectionError, APIStatusError, AuthenticationError, OpenAI, RateLimitError

from app.constants.config import PLACEHOLDER_API_KEYS
from app.constants.invoice_fields import FIELD_KEYS, INVOICE_FIELDS
from app.schemas.invoice_response import empty_invoice


class OpenAIConfigurationError(ValueError):
    pass


class OpenAIService:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key or api_key in PLACEHOLDER_API_KEYS:
            raise OpenAIConfigurationError("OPENAI_API_KEY is not configured")
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")

    def extract_invoice_data(self, invoice_text: str) -> dict[str, Any]:
        """Return {"invoice": {...}, "detected_language": str|None, "confidence": {...}}."""
        prompt = self._build_prompt(invoice_text)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": self._system_prompt()},
                    {"role": "user", "content": prompt},
                ],
            )
        except AuthenticationError as exc:
            raise OpenAIConfigurationError("OPENAI_API_KEY is invalid") from exc
        except (RateLimitError, APIConnectionError, APIStatusError) as exc:
            raise RuntimeError("OPENAI_FAILURE") from exc
        except Exception as exc:
            raise RuntimeError("OPENAI_FAILURE") from exc

        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("OPENAI_FAILURE")

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError("OPENAI_FAILURE") from exc

        return self._normalize_response(parsed)

    def _system_prompt(self) -> str:
        field_descriptions = "\n".join(
            f'- "{field["key"]}": {field["label"]}'
            + (
                f' (must be one of: {", ".join(field["allowed"])})'
                if field.get("allowed")
                else ""
            )
            + (" — date in YYYY-MM-DD format" if field["type"] == "date" else "")
            for field in INVOICE_FIELDS
        )

        return f"""You are a utility invoice data extraction assistant.

Extract structured data from utility invoices that may be written in ANY language
(English, Spanish, French, German, etc.) and in any layout.

Return a single JSON object with these keys:
- "invoice": an object with EXACTLY these fields:
{field_descriptions}
- "detected_language": the ISO 639-1 code of the invoice's primary language (e.g. "en", "es", "fr"), or null.
- "confidence": an object mapping every invoice field name to a number between 0 and 1
  indicating how confident you are in that value (1 = explicitly stated, 0 = absent/guessed).

Extraction rules:
- Translate labels/values to English where appropriate, but keep vendor names as printed.
- Normalize utility_type to exactly one of: electricity, gas, water.
- Normalize ALL dates to YYYY-MM-DD (interpret month names in the invoice's language).
- usage_amount must be numeric only, no units or thousands separators.
- usage_unit is the measurement unit (e.g. kWh, therms, gallons, m3).
- billing_period_start / billing_period_end are the start and end of the billing cycle
  (look for "billing period", "periodo de facturacion", "periode de facturation", date ranges).
  If only a single billing month/range is given, derive both endpoints from it.
- Return null for any field that is not present or cannot be determined confidently.
- Never invent or hallucinate values that are not supported by the invoice text."""

    def _build_prompt(self, invoice_text: str) -> str:
        return f"""Extract invoice data from the following utility invoice text.

Respond with a JSON object containing ALL THREE top-level keys:
1. "invoice" — an object with these keys: {", ".join(FIELD_KEYS)}
2. "detected_language" — the ISO 639-1 code of the invoice's language (e.g. "en", "es", "fr", "de").
3. "confidence" — an object mapping each invoice field to a 0-1 confidence score.

Invoice text:
---
{invoice_text}
---"""

    def _normalize_response(self, parsed: dict[str, Any]) -> dict[str, Any]:
        # The model may return fields nested under "invoice" or at the top level.
        raw_invoice = parsed.get("invoice")
        if not isinstance(raw_invoice, dict):
            raw_invoice = parsed

        numeric_keys = {f["key"] for f in INVOICE_FIELDS if f["type"] == "number"}

        invoice = empty_invoice()
        for key in FIELD_KEYS:
            value = raw_invoice.get(key)
            if value is None or value == "" or value == "null":
                invoice[key] = None
            elif key in numeric_keys:
                try:
                    invoice[key] = float(str(value).replace(",", ""))
                except (TypeError, ValueError):
                    invoice[key] = None
            else:
                invoice[key] = str(value).strip() if value is not None else None

        detected_language = parsed.get("detected_language")
        if isinstance(detected_language, str):
            detected_language = detected_language.strip().lower() or None
        else:
            detected_language = None

        raw_confidence = parsed.get("confidence")
        confidence: dict[str, float] = {}
        if isinstance(raw_confidence, dict):
            for key in FIELD_KEYS:
                try:
                    confidence[key] = round(min(max(float(raw_confidence[key]), 0.0), 1.0), 2)
                except (KeyError, TypeError, ValueError):
                    continue

        return {
            "invoice": invoice,
            "detected_language": detected_language,
            "confidence": confidence,
        }
