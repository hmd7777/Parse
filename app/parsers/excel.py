# app/parsers/excel.py
from pathlib import Path
import pandas as pd

def parse_tabular(path: Path, char_limit: int = 2000) -> str:
    """
    Handles CSV and XLSX by producing a small, readable preview.
    We cap rows to keep it fast for large files.
    """
    suffix = path.suffix.lower()
    try:
        if suffix == ".csv":
            df = pd.read_csv(path, nrows=200)
        else:
            # default: first sheet, cap rows
            df = pd.read_excel(path, nrows=200)
    except Exception as e:
        return f"Failed to read table: {e}"

    if df is None or df.empty:
        return "Empty or unreadable table."

    # Show the first ~20 rows, CSV-formatted. Adjust as you like.
    preview_csv = df.head(20).to_csv(index=False)
    return (preview_csv[:char_limit]).strip()
