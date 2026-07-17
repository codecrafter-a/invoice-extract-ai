from typing import Any

from pydantic import BaseModel, Field

from app.constants.invoice_fields import FIELD_KEYS, INVOICE_FIELDS


class ErrorDetail(BaseModel):
    code: str
    message: str


class ApiResponse(BaseModel):
    success: bool
    data: dict[str, Any] | None = None
    error: ErrorDetail | None = None


class UploadResponse(BaseModel):
    file_id: str


class ValidationWarning(BaseModel):
    field: str
    message: str


class FieldDisplay(BaseModel):
    key: str
    label: str
    type: str
    required: bool
    primary: bool = False


class ExtractResponse(BaseModel):
    invoice: dict[str, Any]
    fields: list[FieldDisplay] = Field(default_factory=list)
    warnings: list[ValidationWarning] = Field(default_factory=list)
    csv_id: str | None = None
    extraction_method: str | None = None
    detected_language: str | None = None
    confidence: dict[str, float] = Field(default_factory=dict)


def get_field_display() -> list[FieldDisplay]:
    return [
        FieldDisplay(
            key=field["key"],
            label=field["label"],
            type=field["type"],
            required=field["required"],
            primary=field.get("primary", False),
        )
        for field in INVOICE_FIELDS
    ]


def empty_invoice() -> dict[str, Any]:
    return {key: None for key in FIELD_KEYS}
