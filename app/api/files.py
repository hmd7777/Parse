# app/api/files.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from app.models import FILES, StoredFile, new_file_id, UPLOAD_DIR
from app.schemas import FileInfo

router = APIRouter(prefix="/files", tags=["files"])

ALLOWED_MIME = {
    "application/pdf",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "application/vnd.ms-excel",  # older excel (some exporters)
}

@router.post("/upload", response_model=FileInfo)
async def upload_file(file: UploadFile = File(...)) -> FileInfo:
    # Basic allow-list; we’ll refine later
    mime = file.content_type or "application/octet-stream"
    if mime not in ALLOWED_MIME:
        # skeleton allows only the above; you can loosen if needed
        raise HTTPException(status_code=415, detail=f"Unsupported media type: {mime}")

    fid = new_file_id()
    dest: Path = UPLOAD_DIR / f"{fid}__{file.filename}"
    size = 0

    # stream to disk to avoid memory spikes
    with dest.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            out.write(chunk)
            size += len(chunk)

    sf = StoredFile(
        id=fid,
        name=file.filename,
        mime=mime,
        size=size,
        path=dest,
        preview=None,  # filled after we add parsers in the next step
    )
    FILES[fid] = sf
    return FileInfo(**sf.__dict__)

@router.get("/{file_id}", response_model=FileInfo)
def get_file(file_id: str) -> FileInfo:
    sf = FILES.get(file_id)
    if not sf:
        raise HTTPException(status_code=404, detail="File not found")
    return FileInfo(**sf.__dict__)
