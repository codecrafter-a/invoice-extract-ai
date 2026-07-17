# AI-Powered Utility Invoice Extraction System

A full-stack application that extracts structured data from utility invoice PDFs using OpenAI GPT-4o, displays results in a React UI, and generates downloadable CSV files.

## 1. Project Overview

Users upload utility invoice PDFs (electricity, gas, or water) through a React web interface. The FastAPI backend extracts text with pdfplumber, sends it to GPT-4o for structured field extraction, validates the results, and generates a downloadable CSV.

### Key Features

- PDF upload via drag-and-drop web UI
- AI-powered extraction with GPT-4o, with an automatic regex fallback when the LLM is unavailable
- Multilingual invoice support (English, Spanish, French, German, …) with automatic language detection
- Per-field confidence scoring surfaced in the UI
- Validation warnings for missing/invalid fields and reversed billing periods
- CSV download with human-readable headers
- Clean layered architecture with a single source of truth for field definitions
- Automated test suite (pytest) and a one-command `./run.sh` launcher

## 2. Architecture Diagram

```
React UI (Vite + Tailwind + Axios)
        ↓
FastAPI Routes
        ↓
Extraction Service (orchestrator)
        ↓
PDF Service → OpenAI Service → Validation Service → CSV Service
```

Data flow:

```
PDF Upload → Text Extraction → GPT-4o → Structured JSON → Validation → CSV
```

## 3. Folder Structure

```
Take Home AI/
├── invoice-extractor-api/          # FastAPI backend
│   ├── app/
│   │   ├── constants/
│   │   │   ├── invoice_fields.py   # Single source of truth (SSOT)
│   │   │   └── config.py
│   │   ├── routes/
│   │   │   └── invoice_routes.py
│   │   ├── schemas/
│   │   │   └── invoice_response.py
│   │   ├── services/
│   │   │   ├── pdf_service.py
│   │   │   ├── openai_service.py
│   │   │   ├── regex_extraction_service.py
│   │   │   ├── validation_service.py
│   │   │   ├── csv_service.py
│   │   │   └── extraction_service.py
│   │   └── utils/
│   │       └── file_utils.py
│   ├── uploads/
│   ├── csv_output/
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── invoice-extractor-ui/           # React frontend
│   └── src/
│       ├── api/
│       │   └── invoiceApi.js
│       ├── components/
│       │   ├── Header.jsx
│       │   ├── FileUpload.jsx
│       │   ├── Loader.jsx
│       │   ├── InvoiceTable.jsx
│       │   └── DownloadCsvButton.jsx
│       ├── hooks/
│       │   └── useInvoice.js
│       ├── pages/
│       │   ├── UploadPage.jsx
│       │   └── ResultsPage.jsx
│       ├── routes/
│       │   └── AppRoutes.jsx
│       ├── App.jsx
│       └── main.jsx
│   ├── tests/                       # pytest automated tests
│   ├── requirements-dev.txt
│   └── pytest.ini
├── invoice-extractor-ui/           # React frontend
├── samples/                        # Sample invoice PDFs (EN, ES, FR, DE)
├── output/
│   └── extracted_invoices.csv       # Generated output from the sample invoices
├── scripts/
│   ├── generate_sample_invoices.py  # Regenerate the sample PDFs
│   └── extract_samples.py           # Batch-extract all samples -> output CSV
├── run.sh                           # One-command launcher (backend + frontend)
└── README.md
```

## 4. Installation Guide

### Prerequisites

- Python 3.10–3.13 (3.14 is not yet supported by the pinned `pydantic-core` wheels)
- Node.js 18+
- OpenAI API key (optional — the app falls back to regex extraction without one)

### Quick Start (one command)

From the project root:

```bash
./run.sh
```

This creates/repairs the Python venv, installs frontend deps if needed, frees ports
8000/5173 if they are in use, and starts both servers. Press Ctrl+C to stop both.
Then open http://localhost:5173.

The manual steps below are equivalent if you prefer to run each service yourself.

### Backend

```bash
cd invoice-extractor-api
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Frontend

```bash
cd invoice-extractor-ui
npm install
cp .env.example .env
```

### Sample PDFs (optional)

```bash
pip install fpdf2
python scripts/generate_sample_invoices.py
```

## 5. Environment Variables

### Backend (`invoice-extractor-api/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_MODEL` | Model to use | `gpt-4o` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:5173` |

### Frontend (`invoice-extractor-ui/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:8000` |

## 6. Running Frontend

```bash
cd invoice-extractor-ui
npm run dev
```

App: http://localhost:5173

## 7. Running Backend

```bash
cd invoice-extractor-api
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## 8. API Documentation

| Method | Path | Description |
|--------|------|-------------|
| POST | `/upload` | Upload PDF, returns `file_id` |
| POST | `/extract` | Extract invoice data from uploaded PDF |
| GET | `/download-csv?csv_id=` | Download generated CSV |
| GET | `/health` | Health check |

### POST /upload

Upload a utility invoice PDF.

**Request:** `multipart/form-data` with `file` field

**Response:**
```json
{
  "success": true,
  "data": {
    "file_id": "uuid-string"
  }
}
```

### POST /extract

Extract structured data from an uploaded PDF.

**Request:**
```json
{
  "file_id": "uuid-string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "invoice": {
      "vendor_name": "Pacific Power & Light",
      "invoice_date": "2025-03-15",
      "service_address": "742 Evergreen Terrace, Springfield, IL 62704",
      "utility_type": "electricity",
      "usage_amount": 847.0,
      "usage_unit": "kWh",
      "billing_period_start": "2025-02-01",
      "billing_period_end": "2025-02-28"
    },
    "fields": [
      { "key": "vendor_name", "label": "Vendor Name", "type": "string", "required": true }
    ],
    "warnings": [],
    "csv_id": "uuid-string",
    "extraction_method": "openai",
    "detected_language": "en",
    "confidence": { "vendor_name": 1.0, "usage_amount": 0.95 }
  }
}
```

### GET /download-csv?csv_id={id}

Download the generated CSV file.

### GET /health

Returns `{ "status": "ok" }`.

## 9. Sample Request/Response

**Upload a PDF:**
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@samples/electricity_bill_english.pdf"
```

**Extract data:**
```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"file_id": "your-file-id-here"}'
```

**Download CSV:**
```bash
curl -O "http://localhost:8000/download-csv?csv_id=your-csv-id-here"
```

## 10. Design Decisions

### Single Source of Truth

All invoice field definitions live in `app/constants/invoice_fields.py`. This file drives OpenAI prompt generation, validation rules, CSV headers, API response field metadata, and response formatting. No field definitions are duplicated elsewhere.

### OpenAI as Primary Engine

GPT-4o is the primary extraction engine. If OpenAI is unavailable, `regex_extraction_service.py` provides pattern-based extraction so the API keeps working.

### Orchestration Layer

`extraction_service.py` coordinates the full pipeline (PDF → OpenAI or Regex → Validation → CSV). Routes stay thin and delegate to this service.

### Separation of Concerns

| Layer | Responsibility |
|-------|---------------|
| `pdf_service.py` | PDF text extraction only |
| `openai_service.py` | Prompt building and GPT-4o calls only |
| `regex_extraction_service.py` | Pattern-based extraction when OpenAI is unavailable |
| `validation_service.py` | Field validation and warnings only |
| `csv_service.py` | CSV generation and storage only |
| `extraction_service.py` | Pipeline orchestration |

### Frontend Architecture

- Components handle UI only
- `useInvoice.js` owns business logic (upload + extract workflow)
- `invoiceApi.js` owns all Axios API calls
- Field labels come from the API (derived from `invoice_fields.py`), not duplicated in the frontend

### Error Handling

- Invalid/empty PDFs return 400 with clear messages
- OpenAI failures return 500 without exposing stack traces or raw API responses
- Validation issues produce warnings, not hard errors

### Extracted Fields

**Spec-required fields:**

| Field | Type | Required |
|-------|------|----------|
| vendor_name | string | Yes |
| invoice_date | date (YYYY-MM-DD) | Yes |
| service_address | string | No |
| utility_type | enum (electricity/gas/water) | Yes |
| usage_amount | number | Yes |
| usage_unit | string | Yes |
| billing_period_start | date (YYYY-MM-DD) | No |
| billing_period_end | date (YYYY-MM-DD) | No |

**Additional fields** commonly present on utility invoices (extracted when available):

| Field | Type | Required |
|-------|------|----------|
| invoice_number | string | No |
| account_number | string | No |
| due_date | date (YYYY-MM-DD) | No |
| total_amount | number | No |
| currency | string | No |
| tax_amount | number | No |
| meter_number | string | No |

Return `null` for fields that cannot be confidently extracted. Do not hallucinate values.
New fields are added in one place — `app/constants/invoice_fields.py` — and automatically flow
into the LLM prompt, validation, CSV columns, API response, and the UI table.

**Assumption:** `billing_period_start` / `billing_period_end` are treated as optional because
some invoices (e.g. minimal receipts) only show an invoice date, not a billing cycle. They are
still extracted whenever present. All other required fields produce a validation warning if missing.

## 11. Output CSV & Batch Extraction

A pre-generated output CSV from all sample invoices is committed at
[`output/extracted_invoices.csv`](output/extracted_invoices.csv). It contains one row per
sample with every extracted field plus the detected language and extraction method.

Regenerate it at any time (uses GPT-4o if a key is configured, otherwise the regex fallback):

```bash
invoice-extractor-api/venv/bin/python scripts/extract_samples.py
```

## 12. Testing Instructions

### Automated Tests

```bash
cd invoice-extractor-api
./venv/bin/pip install -r requirements-dev.txt
./venv/bin/python -m pytest
```

The suite (in `invoice-extractor-api/tests/`) covers, with **no network calls**:

- Validation rules — required fields, date/number/enum formats, negative usage, reversed billing periods
- Regex fallback extraction across English and Spanish, including billing periods and language detection
- OpenAI response normalization — nested vs. flat JSON, number coercion, confidence clamping
- CSV generation and single-source-of-truth field alignment

### How Accuracy Was Validated

The 6 sample invoices were run end-to-end and the output CSV was inspected field-by-field
against the known source values. Coverage spans:

- **Languages:** English, Spanish, French, German (label + month-name translation)
- **Layouts:** detailed vs. minimal; labeled vs. inline usage (`Electric - 520 kWh`)
- **Date formats:** ISO (`2025-02-01`), numeric (`01/02/2025`, `28.02.2025`), textual (`10 de marzo de 2025`, `5 mars 2025`)
- **Missing fields:** two samples omit the billing period on purpose to confirm graceful nulls

### Manual Testing

1. Generate sample PDFs: `python scripts/generate_sample_invoices.py`
2. Start the app: `./run.sh` (see sections 6/7 for the manual equivalent)
3. Upload each sample PDF through the UI at http://localhost:5173
4. Verify extracted fields, detected language, and confidence on the Results page
5. Download and inspect the CSV output
6. Confirm validation warnings appear for incomplete invoices

### Error Case Testing

| Test | Expected Result |
|------|----------------|
| Upload a non-PDF file | "Only PDF files are supported" |
| Upload an empty file | "The uploaded PDF is empty" |
| Extract with invalid file_id | "Uploaded file not found" |
| Missing OPENAI_API_KEY | "OPENAI_API_KEY is not configured" |
