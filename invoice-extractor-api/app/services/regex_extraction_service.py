import re
from datetime import datetime
from typing import Any

from app.schemas.invoice_response import empty_invoice

MONTH_MAP = {
    "january": "01", "jan": "01", "enero": "01",
    "february": "02", "feb": "02", "febrero": "02",
    "march": "03", "mar": "03", "marzo": "03", "mars": "03",
    "april": "04", "apr": "04", "abril": "04", "avril": "04",
    "may": "05", "mayo": "05", "mai": "05",
    "june": "06", "jun": "06", "junio": "06", "juin": "06",
    "july": "07", "jul": "07", "julio": "07", "juillet": "07",
    "august": "08", "aug": "08", "agosto": "08", "aout": "08",
    "september": "09", "sep": "09", "sept": "09", "septiembre": "09",
    "october": "10", "oct": "10", "octubre": "10", "octobre": "10",
    "november": "11", "nov": "11", "noviembre": "11", "novembre": "11",
    "december": "12", "dec": "12", "diciembre": "12", "decembre": "12",
    "janvier": "01", "janv": "01",
    "fevrier": "02", "fev": "02",
    "1er": "01",
}


class RegexExtractionService:
    def extract_invoice_data(self, invoice_text: str) -> dict[str, Any]:
        result = empty_invoice()
        lines = [line.strip() for line in invoice_text.splitlines() if line.strip()]

        result["vendor_name"] = self._extract_vendor_name(lines)
        result["invoice_date"] = self._extract_invoice_date(invoice_text)
        result["service_address"] = self._extract_service_address(invoice_text)
        result["utility_type"] = self._extract_utility_type(invoice_text)
        usage_amount, usage_unit = self._extract_usage(invoice_text)
        result["usage_amount"] = usage_amount
        result["usage_unit"] = usage_unit
        start, end = self._extract_billing_period(invoice_text)
        result["billing_period_start"] = start
        result["billing_period_end"] = end

        # Regex only fills fields it can match, so confidence is high (0.9) for a
        # matched field and 0 otherwise. This is deliberately conservative.
        confidence = {key: (0.9 if result[key] is not None else 0.0) for key in result}

        return {
            "invoice": result,
            "detected_language": self._detect_language(invoice_text),
            "confidence": confidence,
        }

    def _extract_vendor_name(self, lines: list[str]) -> str | None:
        skip_prefixes = (
            "invoice", "factura", "facture", "utility", "billing", "date",
            "service", "period", "type", "energy", "consumption", "thank",
            "gracias", "merci",
        )
        for line in lines[:3]:
            lower = line.lower()
            if any(lower.startswith(prefix) for prefix in skip_prefixes):
                continue
            if len(line) >= 3:
                return line
        return lines[0] if lines else None

    def _extract_invoice_date(self, text: str) -> str | None:
        patterns = [
            r"invoice\s*date\s*[:#]?\s*([^\n]+)",
            r"fecha\s+de\s+factura\s*[:#]?\s*([^\n]+)",
            r"date\s+de\s+facture\s*[:#]?\s*([^\n]+)",
            r"date\s*[:#]?\s*([^\n]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parsed = self._parse_date(match.group(1))
                if parsed:
                    return parsed
        return None

    def _extract_service_address(self, text: str) -> str | None:
        patterns = [
            r"service\s+address\s*[:#]?\s*([^\n]+)",
            r"direccion\s+de\s+servicio\s*[:#]?\s*([^\n]+)",
            r"adresse\s+de\s+service\s*[:#]?\s*([^\n]+)",
            r"service\s+location\s*[:#]?\s*([^\n]+)",
            r"address\s*[:#]?\s*([^\n]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_utility_type(self, text: str) -> str | None:
        lower = text.lower()
        if re.search(r"\b(electricity|electric|electrico|electrique)\b", lower):
            return "electricity"
        if re.search(r"\b(natural\s+gas|(?<!natural\s)gas)\b", lower):
            return "gas"
        if re.search(r"\b(water|eau|agua)\b", lower):
            return "water"
        return None

    def _extract_usage(self, text: str) -> tuple[float | None, str | None]:
        patterns = [
            r"(?:energy\s+consumption|consumo|consommation|usage|consumption)\s*[:#]?\s*([\d,.]+)\s*([a-zA-Z0-9³]+)",
            r"(?:natural\s+gas\s+usage)\s*[:#]?\s*([\d,.]+)\s*([a-zA-Z0-9³]+)",
            r"(?:electric)\s*[-–]\s*([\d,.]+)\s*([a-zA-Z0-9³]+)",
            r"([\d,.]+)\s*(kwh|therms?|gallons?|m3|m³)\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = float(match.group(1).replace(",", ""))
                unit = match.group(2).replace("³", "3")
                return amount, unit
        return None, None

    # Date tokens: ISO (2025-02-01), numeric (01/02/2025, 28.02.2025) or textual
    # (1 fevrier 2025). Kept separate from the range separator so the "-" inside
    # an ISO date is never mistaken for a range delimiter.
    _DATE_TOKEN = re.compile(
        r"\d{4}-\d{2}-\d{2}"
        r"|\d{1,2}[/.]\d{1,2}[/.]\d{2,4}"
        r"|\d{1,2}(?:er)?(?:\s+de)?\s+[a-zA-Zà-ÿ]+(?:\s+de)?\s+\d{4}",
        re.IGNORECASE,
    )

    def _extract_billing_period(self, text: str) -> tuple[str | None, str | None]:
        label = re.compile(
            r"(?:billing\s+period|billing\s+cycle|service\s+period|"
            r"periodo\s+de\s+facturaci[oó]n|per[ií]odo\s+de\s+facturaci[oó]n|"
            r"p[eé]riode\s+de\s+facturation|abrechnungszeitraum)"
            r"\s*[:#]?\s*(.+)",
            re.IGNORECASE,
        )
        match = label.search(text)
        if match:
            dates = [self._parse_date(tok) for tok in self._DATE_TOKEN.findall(match.group(1))]
            dates = [d for d in dates if d]
            if len(dates) >= 2:
                return dates[0], dates[1]
            if len(dates) == 1:
                return dates[0], None

        return None, None

    def _detect_language(self, text: str) -> str | None:
        lower = text.lower()
        markers = {
            "es": ("factura", "consumo", "direccion", "dirección", "servicio", "gracias"),
            "fr": ("facture", "consommation", "adresse", "eau", "merci", "période"),
            "de": ("rechnung", "verbrauch", "adresse", "zeitraum"),
            "en": ("invoice", "usage", "address", "billing", "consumption", "thank"),
        }
        scores = {
            lang: sum(1 for word in words if word in lower)
            for lang, words in markers.items()
        }
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else None

    def _parse_date(self, value: str) -> str | None:
        value = value.strip().rstrip(".,")
        iso_match = re.search(r"(\d{4})-(\d{2})-(\d{2})", value)
        if iso_match:
            return f"{iso_match.group(1)}-{iso_match.group(2)}-{iso_match.group(3)}"

        numeric_match = re.search(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", value)
        if numeric_match:
            day, month, year = numeric_match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        text_match = re.search(
            r"(\d{1,2})(?:er)?(?:\s+de)?\s+([a-zA-Z]+)(?:\s+de)?\s+(\d{4})|"
            r"([a-zA-Z]+)\s+(\d{1,2}),?\s+(\d{4})",
            value,
            re.IGNORECASE,
        )
        if not text_match:
            return None

        if text_match.group(1):
            day, month_name, year = text_match.group(1), text_match.group(2), text_match.group(3)
        else:
            month_name, day, year = text_match.group(4), text_match.group(5), text_match.group(6)

        month = MONTH_MAP.get(month_name.lower())
        if not month:
            return None

        try:
            datetime.strptime(f"{year}-{month}-{day.zfill(2)}", "%Y-%m-%d")
            return f"{year}-{month}-{day.zfill(2)}"
        except ValueError:
            return None
