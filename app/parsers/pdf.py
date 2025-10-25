# app/parsers/pdf.py
from pathlib import Path
import fitz  # PyMuPDF

def parse_pdf(path: Path, char_limit: int = 2000) -> str:
    text_parts: list[str] = []
    with fitz.open(path) as doc:
        for page in doc:
            # "text" gives layout-aware extraction; fallback to "text" (same here)
            t = page.get_text("text")
            if t:
                text_parts.append(t)
            if sum(len(p) for p in text_parts) >= char_limit:
                break
    full = "".join(text_parts).strip()
    if not full:
        return "No text detected in PDF (might be scanned)."
    return full[:char_limit]
