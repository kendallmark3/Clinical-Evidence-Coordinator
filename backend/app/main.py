from pathlib import Path
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import TypeAdapter, ValidationError

from backend.app.config import settings
from backend.app.documents.pdf_text import extract_text
from backend.app.models import ProtocolRequirement, StudyPackage, ReviewResponse
from backend.app.orchestration.orchestrator import Orchestrator
from backend.app.providers.factory import get_provider

FRONTEND = Path(__file__).resolve().parents[2] / "frontend" / "index.html"
MAX_FILES = 20
MAX_FILE_BYTES = 10 * 1024 * 1024

app = FastAPI(
    title="Clinical Evidence Coordinator",
    version="0.2.0",
    description="Synthetic clinical-study evidence package orchestration demo.",
)

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(FRONTEND)

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/config/status")
def config_status():
    return {
        "provider_mode": settings.provider_mode,
        "aws_region": settings.aws_region,
        "bedrock_configured": bool(settings.bedrock_model_id),
        "synthetic_data_only": True,
    }

@app.post("/api/review", response_model=ReviewResponse)
def review(package: StudyPackage):
    orchestrator = Orchestrator(settings.artifact_dir)
    return orchestrator.run(package.model_dump())

@app.post("/api/review/documents", response_model=ReviewResponse)
async def review_documents(
    study_id: str = Form(...),
    title: str = Form(...),
    requirements: str = Form(..., description="JSON array of protocol requirements"),
    files: List[UploadFile] = File(...),
):
    try:
        reqs = TypeAdapter(List[ProtocolRequirement]).validate_json(requirements)
    except ValidationError as exc:
        raise HTTPException(422, f"Invalid requirements: {exc.errors(include_url=False)}")
    if not reqs:
        raise HTTPException(422, "At least one requirement is needed.")
    if len(files) > MAX_FILES:
        raise HTTPException(422, f"At most {MAX_FILES} files per review.")

    documents = []
    for upload in files:
        data = await upload.read(MAX_FILE_BYTES + 1)
        if len(data) > MAX_FILE_BYTES:
            raise HTTPException(413, f"{upload.filename} is larger than 10 MB.")
        if not data.startswith(b"%PDF"):
            raise HTTPException(422, f"{upload.filename} is not a PDF.")
        documents.append({"filename": upload.filename, "text": extract_text(data)})

    orchestrator = Orchestrator(settings.artifact_dir, get_provider(settings))
    return orchestrator.run_documents(
        study_id, title, [r.model_dump() for r in reqs], documents
    )
