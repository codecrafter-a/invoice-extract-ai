#!/usr/bin/env python3
"""Batch-extract every sample invoice and write a combined output CSV.

Runs the same extraction pipeline the web app uses (GPT-4o when an OPENAI_API_KEY
is configured, otherwise the regex fallback) over every PDF in samples/ and writes
the results to output/extracted_invoices.csv.

Usage:
    invoice-extractor-api/venv/bin/python scripts/extract_samples.py
"""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API_DIR = ROOT / "invoice-extractor-api"
SAMPLES_DIR = ROOT / "samples"
OUTPUT_DIR = ROOT / "output"

# Make the backend package importable and load its .env.
sys.path.insert(0, str(API_DIR))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(API_DIR / ".env", override=True)

from app.constants.invoice_fields import CSV_HEADERS, FIELD_KEYS  # noqa: E402
from app.services.extraction_service import ExtractionService  # noqa: E402


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    service = ExtractionService()

    pdfs = sorted(SAMPLES_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {SAMPLES_DIR}")
        return

    combined_path = OUTPUT_DIR / "extracted_invoices.csv"
    header = ["Source File", *CSV_HEADERS, "Detected Language", "Extraction Method", "Warnings"]

    with combined_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)

        for pdf in pdfs:
            try:
                result = service.process_invoice(pdf)
            except Exception as exc:  # noqa: BLE001 - report and continue
                print(f"  ! {pdf.name}: FAILED ({exc})")
                continue

            warnings = "; ".join(w.message for w in result.warnings)
            row = [
                pdf.name,
                *[result.invoice.get(key) for key in FIELD_KEYS],
                result.detected_language or "",
                result.extraction_method,
                warnings,
            ]
            writer.writerow(row)
            print(f"  + {pdf.name}: {result.extraction_method} / {result.detected_language or 'n/a'}")

    print(f"\nWrote combined CSV: {combined_path}")


if __name__ == "__main__":
    main()
