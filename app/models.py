# app/models.py
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict
from uuid import uuid4

UPLOAD_DIR = Path(".data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class StoredFile:
    id: str
    name: str
    mime: str
    size: int
    path: Path
    preview: Optional[str] = None  # will be filled in later stages

# naive in-memory store for Stage 1
FILES: Dict[str, StoredFile] = {}

def new_file_id() -> str:
    return uuid4().hex
