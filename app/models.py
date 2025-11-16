# app/models.py
from dataclasses import dataclass
from datetime import datetime
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


@dataclass
class Job:
    """
    Lightweight in-memory representation of a background parsing job.

    The actual task execution and result are handled by Celery; this structure
    simply tracks metadata we care about on the API side.
    """

    id: str  # Celery task id
    file_name: str
    mime: str
    created_at: datetime
    updated_at: datetime
    status: str = "PENDING"
    preview: Optional[str] = None
    error: Optional[str] = None


JOBS: Dict[str, Job] = {}


def new_file_id() -> str:
    return uuid4().hex


def new_job_id() -> str:
    return uuid4().hex
