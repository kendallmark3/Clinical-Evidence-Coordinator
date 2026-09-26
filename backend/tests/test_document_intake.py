import json
from dataclasses import replace
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from backend.app import main
from backend.app.documents.pdf_text import extract_text
from backend.app.orchestration.orchestrator import Orchestrator
from backend.app.providers.base import Provider
from backend.app.providers.mock_provider import MockProvider

SAMPLES = Path(__file__).resolve().parents[2] / "samples"
DOCS = SAMPLES / "documents"
REQUIREMENTS = json.loads((SAMPLES / "study-package-complete.json").read_text())["protocol_requirements"]
FINAL_SET = [
    "protocol-v1.pdf",
    "device-verification-results.pdf",
    "adverse-event-reconciliation.pdf",
    "site-completion-summary.pdf",
]

class FixedProvider(Provider):
    name = "fixed"

    def __init__(self, response):
        self.response = response

    def generate(self, prompt, system=""):
        if isinstance(self.response, Exception):
            raise self.response
        return self.response

def documents(*names):
    return [{"filename": n, "text": extract_text((DOCS / n).read_bytes())} for n in names]

def review(tmp_path, docs, provider=None):
    return Orchestrator(str(tmp_path), provider or MockProvider()).run_documents(
        "SYN-CEC-DOC", "Synthetic", REQUIREMENTS, docs
    )

def test_complete_document_set_is_ready(tmp_path):
    result = review(tmp_path, documents(*FINAL_SET))
    assert result["status"] == "READY_FOR_HUMAN_REVIEW"
    assert result["artifacts"]["document_intake"]["classifications"][0]["classified_by"] == "mock"

def test_missing_adverse_event_record_fails_closed(tmp_path):
    result = review(tmp_path, documents(*[n for n in FINAL_SET if "adverse" not in n]))
    assert result["status"] == "NOT_READY_FOR_HUMAN_REVIEW"
    assert result["missing_requirement_ids"] == ["REQ-003"]

def test_draft_adverse_event_record_fails_closed(tmp_path):
    docs = documents(*[n.replace("reconciliation.pdf", "reconciliation-draft.pdf") for n in FINAL_SET])
    result = review(tmp_path, docs)
    assert result["status"] == "NOT_READY_FOR_HUMAN_REVIEW"
    assert result["missing_requirement_ids"] == ["REQ-003"]

def test_unrelated_document_maps_to_nothing(tmp_path):
    result = review(tmp_path, documents(*FINAL_SET, "facilities-parking-memo.pdf"))
    memo = result["artifacts"]["document_intake"]["evidence_items"][-1]
    assert memo["requirement_ids"] == []
    assert result["status"] == "READY_FOR_HUMAN_REVIEW"

@pytest.mark.parametrize("response", [
    "not json at all",
    '{"requirement_ids": "REQ-001", "status": "complete"}',
    '{"requirement_ids": ["REQ-001"], "status": "approved"}',
    RuntimeError("Bedrock unavailable"),
])
def test_bad_model_output_fails_closed(tmp_path, response):
    result = review(tmp_path, documents(*FINAL_SET), FixedProvider(response))
    assert result["status"] == "NOT_READY_FOR_HUMAN_REVIEW"
    for item in result["artifacts"]["document_intake"]["classifications"]:
        assert item["error"]

def test_model_cannot_invent_requirements(tmp_path):
    invented = '{"requirement_ids": ["REQ-001", "REQ-002", "REQ-003", "REQ-004", "REQ-999"], "status": "complete"}'
    result = review(tmp_path, documents("protocol-v1.pdf"), FixedProvider(invented))
    assert result["status"] == "NOT_READY_FOR_HUMAN_REVIEW"
    assert any("REQ-999" in f for f in result["blocking_findings"])

def test_upload_endpoint(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "settings", replace(main.settings, artifact_dir=str(tmp_path), provider_mode="mock"))
    client = TestClient(main.app)
    files = [("files", (n, (DOCS / n).read_bytes(), "application/pdf")) for n in FINAL_SET]
    response = client.post("/api/review/documents", data={
        "study_id": "SYN-CEC-DOC",
        "title": "Synthetic",
        "requirements": json.dumps(REQUIREMENTS),
    }, files=files)
    assert response.status_code == 200
    assert response.json()["status"] == "READY_FOR_HUMAN_REVIEW"

def test_upload_endpoint_rejects_non_pdf(tmp_path):
    client = TestClient(main.app)
    response = client.post("/api/review/documents", data={
        "study_id": "S", "title": "T", "requirements": json.dumps(REQUIREMENTS),
    }, files=[("files", ("notes.txt", b"hello", "text/plain"))])
    assert response.status_code == 422

def test_index_page_is_served():
    assert "Clinical Evidence Coordinator" in TestClient(main.app).get("/").text
