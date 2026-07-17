import csv
from pathlib import Path
from typing import Any

from app.constants.invoice_fields import CSV_HEADERS, FIELD_KEYS
from app.utils.file_utils import generate_id, get_csv_path


class CsvService:
    def generate_csv(self, invoice_data: dict[str, Any]) -> tuple[str, Path]:
        csv_id = generate_id()
        file_path = get_csv_path(csv_id)

        try:
            with file_path.open("w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(CSV_HEADERS)
                writer.writerow([invoice_data.get(key) for key in FIELD_KEYS])

            return csv_id, file_path
        except Exception as exc:
            if file_path.exists():
                file_path.unlink()
            raise RuntimeError("CSV_FAILURE") from exc

    def get_csv_file_path(self, csv_id: str) -> Path | None:
        file_path = get_csv_path(csv_id)
        return file_path if file_path.exists() else None
