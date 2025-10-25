# app/api/files.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from app.models import FILES, StoredFile, new_file_id, UPLOAD_DIR
from app.schemas import FileInfo

# NEW: import parsers
from app.parsers.pdf import parse_pdf
from app.parsers.excel import parse_tabular

router = APIRouter(prefix="/files", tags=["files"])

ALLOWED_MIME = {
    "application/pdf",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "application/vnd.ms-excel",
}

PREVIEW_CHARS = 2000
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB cap to keep uploads small

@router.post("/upload", response_model=FileInfo)
async def upload_file(file: UploadFile = File(...)) -> FileInfo:
    mime = file.content_type or "application/octet-stream"
    if mime not in ALLOWED_MIME:
        raise HTTPException(status_code=415, detail=f"Unsupported media type: {mime}")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing original file name")

    fid = new_file_id()
    dest: Path = UPLOAD_DIR / f"{fid}__{file.filename}"
    size = 0

    try:
        with dest.open("wb") as out:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail="File too large; maximum upload size is 5 MB",
                    )
                out.write(chunk)
    except HTTPException:
        if dest.exists():
            dest.unlink()
        raise
    except Exception:
        if dest.exists():
            dest.unlink()
        raise

    # Decide which parser to use
    preview: str | None = None
    try:
        if mime == "application/pdf":
            preview = parse_pdf(dest, char_limit=PREVIEW_CHARS)
        else:
            # CSV or XLSX (or legacy Excel)
            preview = parse_tabular(dest, char_limit=PREVIEW_CHARS)
    except Exception as e:
        preview = f"Parsing failed: {e}"

    sf = StoredFile(
        id=fid,
        name=file.filename,
        mime=mime,
        size=size,
        path=dest,
        preview=preview,
    )
    FILES[fid] = sf
    return FileInfo(**sf.__dict__)

@router.get("/{file_id}", response_model=FileInfo)
def get_file(file_id: str) -> FileInfo:
    sf = FILES.get(file_id)
    if not sf:
        raise HTTPException(status_code=404, detail="File not found")
    return FileInfo(**sf.__dict__)

@router.get("/", response_model=list[FileInfo])
def list_files() -> list[FileInfo]:
    return [FileInfo(**sf.__dict__) for sf in FILES.values()]


@router.delete("/{file_id}", response_model=FileInfo)
def delete_file(file_id: str) -> FileInfo:
    sf = FILES.get(file_id)
    if not sf:
        raise HTTPException(status_code=404, detail="File not found")

    if sf.path.exists():
        try:
            sf.path.unlink()
        except OSError as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to remove file from disk: {exc}",
            ) from exc

    FILES.pop(file_id, None)
    return FileInfo(**sf.__dict__)
