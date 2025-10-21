# app/schemas.py
from pydantic import BaseModel

class FileInfo(BaseModel):
    id: str
    name: str
    mime: str
    size: int
    preview: str | None = None
