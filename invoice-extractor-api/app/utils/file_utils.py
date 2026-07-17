import uuid
from pathlib import Path

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
CSV_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "csv_output"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CSV_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf"}


def generate_id() -> str:
    return str(uuid.uuid4())


def save_upload(file_bytes: bytes, original_filename: str) -> tuple[str, Path]:
    file_id = generate_id()
    extension = Path(original_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("INVALID_PDF")

    file_path = UPLOAD_DIR / f"{file_id}{extension}"
    file_path.write_bytes(file_bytes)
    return file_id, file_path


def get_upload_path(file_id: str) -> Path | None:
    for extension in ALLOWED_EXTENSIONS:
        file_path = UPLOAD_DIR / f"{file_id}{extension}"
        if file_path.exists():
            return file_path
    return None


def get_csv_path(csv_id: str) -> Path:
    return CSV_OUTPUT_DIR / f"{csv_id}.csv"
