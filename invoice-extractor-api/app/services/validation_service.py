import re
from datetime import datetime
from typing import Any

from app.constants.invoice_fields import INVOICE_FIELDS
from app.schemas.invoice_response import ValidationWarning


class ValidationService:
    DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def validate(self, invoice_data: dict[str, Any]) -> tuple[dict[str, Any], list[ValidationWarning]]:
        warnings: list[ValidationWarning] = []
        validated = dict(invoice_data)

        for field in INVOICE_FIELDS:
            key = field["key"]
            value = validated.get(key)
            field_type = field["type"]

            if field["required"] and self._is_missing(value):
                warnings.append(
                    ValidationWarning(
                        field=key,
                        message=f"{field['label']} is required but was not found.",
                    )
                )
                continue

            if self._is_missing(value):
                continue

            if field_type == "date":
                normalized, warning = self._validate_date(key, field["label"], value)
                validated[key] = normalized
                if warning:
                    warnings.append(warning)

            elif field_type == "number":
                normalized, warning = self._validate_number(key, field["label"], value)
                validated[key] = normalized
                if warning:
                    warnings.append(warning)

            elif field_type == "enum":
                normalized, warning = self._validate_enum(
                    key, field["label"], value, field.get("allowed", [])
                )
                validated[key] = normalized
                if warning:
                    warnings.append(warning)

        self._validate_billing_period(validated, warnings)

        return validated, warnings

    def _validate_billing_period(
        self, validated: dict[str, Any], warnings: list[ValidationWarning]
    ) -> None:
        start = validated.get("billing_period_start")
        end = validated.get("billing_period_end")
        if not start or not end:
            return
        try:
            start_date = datetime.strptime(str(start), "%Y-%m-%d")
            end_date = datetime.strptime(str(end), "%Y-%m-%d")
        except ValueError:
            return
        if start_date > end_date:
            warnings.append(
                ValidationWarning(
                    field="billing_period_end",
                    message="Billing period end is before the start date.",
                )
            )

    def _is_missing(self, value: Any) -> bool:
        return value is None or (isinstance(value, str) and not value.strip())

    def _validate_date(
        self, key: str, label: str, value: Any
    ) -> tuple[str | None, ValidationWarning | None]:
        date_str = str(value).strip()

        if not self.DATE_PATTERN.match(date_str):
            return None, ValidationWarning(
                field=key,
                message=f"{label} has an invalid date format. Expected YYYY-MM-DD.",
            )

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str, None
        except ValueError:
            return None, ValidationWarning(
                field=key,
                message=f"{label} is not a valid date.",
            )

    def _validate_number(
        self, key: str, label: str, value: Any
    ) -> tuple[float | None, ValidationWarning | None]:
        try:
            numeric_value = float(value)
            if numeric_value < 0:
                return None, ValidationWarning(
                    field=key,
                    message=f"{label} must be a non-negative number.",
                )
            return numeric_value, None
        except (TypeError, ValueError):
            return None, ValidationWarning(
                field=key,
                message=f"{label} must be a valid number.",
            )

    def _validate_enum(
        self, key: str, label: str, value: Any, allowed: list[str]
    ) -> tuple[str | None, ValidationWarning | None]:
        normalized = str(value).strip().lower()
        if normalized not in allowed:
            return None, ValidationWarning(
                field=key,
                message=f"{label} must be one of: {', '.join(allowed)}.",
            )
        return normalized, None
