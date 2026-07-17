import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from app.constants.config import PLACEHOLDER_API_KEYS
from app.schemas.invoice_response import ValidationWarning
from app.services.csv_service import CsvService
from app.services.openai_service import OpenAIConfigurationError, OpenAIService
from app.services.pdf_service import PdfService
from app.services.regex_extraction_service import RegexExtractionService
from app.services.validation_service import ValidationService

ExtractionMethod = Literal["openai", "regex"]


@dataclass
class ExtractionResult:
    invoice: dict[str, Any]
    warnings: list[ValidationWarning]
    csv_id: str
    extraction_method: ExtractionMethod
    detected_language: str | None = None
    confidence: dict[str, float] = field(default_factory=dict)


class ExtractionService:
    def __init__(self) -> None:
        self.pdf_service = PdfService()
        self.regex_service = RegexExtractionService()
        self.validation_service = ValidationService()
        self.csv_service = CsvService()

    def process_invoice(self, file_path: Path) -> ExtractionResult:
        invoice_text = self.pdf_service.extract_text(file_path)
        extracted, extraction_method = self._extract_invoice_data(invoice_text)
        validated_data, warnings = self.validation_service.validate(extracted["invoice"])
        csv_id, _ = self.csv_service.generate_csv(validated_data)
        return ExtractionResult(
            invoice=validated_data,
            warnings=warnings,
            csv_id=csv_id,
            extraction_method=extraction_method,
            detected_language=extracted.get("detected_language"),
            confidence=extracted.get("confidence", {}),
        )

    def _extract_invoice_data(
        self, invoice_text: str
    ) -> tuple[dict[str, Any], ExtractionMethod]:
        if self._has_openai_key():
            try:
                data = OpenAIService().extract_invoice_data(invoice_text)
                return data, "openai"
            except (OpenAIConfigurationError, RuntimeError):
                pass

        data = self.regex_service.extract_invoice_data(invoice_text)
        return data, "regex"

    def _has_openai_key(self) -> bool:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        return bool(api_key) and api_key not in PLACEHOLDER_API_KEYS
