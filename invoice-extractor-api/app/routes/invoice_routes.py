from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.schemas.invoice_response import (
    ApiResponse,
    ErrorDetail,
    ExtractResponse,
    UploadResponse,
    get_field_display,
)
from app.services.extraction_service import ExtractionService
from app.utils.file_utils import get_upload_path, save_upload

router = APIRouter()
extraction_service = ExtractionService()

UPLOAD_ERRORS = {
    "INVALID_PDF": "The uploaded file is not a valid PDF.",
    "EMPTY_PDF": "The uploaded PDF is empty.",
}

EXTRACT_ERRORS = {
    "INVALID_PDF": "Unable to read the PDF file.",
    "EMPTY_PDF": "No extractable text found in the PDF.",
}

RUNTIME_ERRORS = {
    "OPENAI_FAILURE": "AI extraction failed. Please try again later.",
    "CSV_FAILURE": "Failed to generate CSV file.",
}


def _error_response(code: str, message: str, status_code: int) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=ApiResponse(
            success=False,
            error=ErrorDetail(code=code, message=message),
        ).model_dump(),
    )


def _raise_value_error(exc: ValueError, messages: dict[str, str], default: str) -> None:
    code = str(exc)
    raise _error_response(code, messages.get(code, default), 400) from exc


@router.post("/upload", response_model=ApiResponse)
async def upload_invoice(file: UploadFile = File(...)) -> ApiResponse:
    if not file.filename:
        raise _error_response("INVALID_PDF", "No file was provided.", 400)

    if not file.filename.lower().endswith(".pdf"):
        raise _error_response("INVALID_PDF", "Only PDF files are supported.", 400)

    try:
        file_bytes = await file.read()
        if not file_bytes:
            raise ValueError("EMPTY_PDF")

        file_id, _ = save_upload(file_bytes, file.filename)
        return ApiResponse(
            success=True,
            data=UploadResponse(file_id=file_id).model_dump(),
        )
    except ValueError as exc:
        _raise_value_error(exc, UPLOAD_ERRORS, "Upload failed.")
    except Exception as exc:
        raise _error_response("UPLOAD_FAILURE", "Failed to upload the file.", 500) from exc


@router.post("/extract", response_model=ApiResponse)
async def extract_invoice(body: dict[str, Any]) -> ApiResponse:
    file_id = str(body.get("file_id", "")).strip()
    if not file_id:
        raise _error_response("INVALID_REQUEST", "file_id is required.", 400)

    file_path = get_upload_path(file_id)
    if not file_path:
        raise _error_response("FILE_NOT_FOUND", "Uploaded file not found. Please upload again.", 404)

    try:
        result = extraction_service.process_invoice(file_path)
    except ValueError as exc:
        _raise_value_error(exc, EXTRACT_ERRORS, "PDF processing failed.")
    except RuntimeError as exc:
        code = str(exc)
        raise _error_response(
            code, RUNTIME_ERRORS.get(code, "Extraction failed."), 500
        ) from exc

    return ApiResponse(
        success=True,
        data=ExtractResponse(
            invoice=result.invoice,
            fields=get_field_display(),
            warnings=result.warnings,
            csv_id=result.csv_id,
            extraction_method=result.extraction_method,
            detected_language=result.detected_language,
            confidence=result.confidence,
        ).model_dump(),
    )


@router.get("/download-csv")
async def download_csv(csv_id: str):
    file_path = extraction_service.csv_service.get_csv_file_path(csv_id)
    if not file_path:
        raise _error_response("FILE_NOT_FOUND", "CSV file not found.", 404)

    return FileResponse(
        path=file_path,
        media_type="text/csv",
        filename=f"invoice_{csv_id}.csv",
    )
