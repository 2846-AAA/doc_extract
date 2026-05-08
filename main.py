from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.logger import setup_logger
from app.db.database import init_db

setup_logger()

app = FastAPI(
    title="Document Extraction Platform",
    description="Extract structured data from Aadhaar, Passport, DL, Invoice, PAN",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/")
def root():
    return {"message": "Document Extraction API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
