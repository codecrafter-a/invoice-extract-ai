import re
from pathlib import Path

import pdfplumber


class PdfService:
    def extract_text(self, file_path: Path) -> str:
        try:
            pages: list[str] = []

            with pdfplumber.open(file_path) as pdf:
                if not pdf.pages:
                    raise ValueError("EMPTY_PDF")

                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        pages.append(page_text)

            if not pages:
                raise ValueError("EMPTY_PDF")

            return self._clean_text("\n".join(pages))
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError("INVALID_PDF") from exc

    def _clean_text(self, text: str) -> str:
        text = text.replace("\x00", "")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
