# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.files import router as files_router  # <-- add this

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

@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}

@app.get("/", include_in_schema=False)
def root_to_docs():
    return RedirectResponse(url="/docs")

# register routes
app.include_router(files_router)
