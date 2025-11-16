# app/schemas.py
from pydantic import BaseModel


class FileInfo(BaseModel):
    id: str
    name: str
    mime: str
    size: int
    preview: str | None = None


class JobInfo(BaseModel):
    id: str
    file_name: str
    mime: str
    status: str
    preview: str | None = None
    error: str | None = None
