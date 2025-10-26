# app/main.py
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from starlette.requests import Request

from app.api import files as files_api  # reusable upload logic and router
from app.models import FILES

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))
app = FastAPI(
    title="Parse – Stage 1 (API)",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "frontend" / "static")),
    name="static",
)

DEFAULT_PROMPT = (
    "Review the provided document to determine the average number of hours "
    "people in Madrid, London, New York, Paris, Milan, Barcelona, Tokyo, "
    "Istanbul, Seoul and Los Angeles typically spend on their phones. Then, "
    "create line charts to visualise this data, accompanied by explanatory "
    "text describing the trends shown in the charts. Finally, present both the "
    "charts and the accompanying text using dark mode background colours."
)

def _latest_file(file_id: str | None = None):
    if file_id:
        return FILES.get(file_id)
    if not FILES:
        return None
    return list(FILES.values())[-1]

@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}

@app.get("/", include_in_schema=False)
async def show_home(request: Request, file_id: str | None = None):
    selected = _latest_file(file_id)
    context = {
        "request": request,
        "user_prompt": DEFAULT_PROMPT,
        "file_name": None,
        "preview_snippet": None,
    }

    if selected:
        preview = (selected.preview or "").strip()
        if preview:
            preview = " ".join(preview.split())
        snippet = preview[:300] if preview else ""
        if preview and len(preview) > 300:
            snippet = snippet.rstrip() + "..."

        if snippet:
            context["user_prompt"] = snippet
            context["preview_snippet"] = snippet

        context["file_name"] = selected.name
        return templates.TemplateResponse("right_report.html", context)

    return templates.TemplateResponse("right_home.html", context)

@app.post("/upload-file", include_in_schema=False)
async def upload_file_view(request: Request, file: UploadFile = File(...)):
    info = await files_api.upload_file(file)
    return RedirectResponse(url=f"/?file_id={info.id}", status_code=303)

# register routes
app.include_router(files_api.router)
