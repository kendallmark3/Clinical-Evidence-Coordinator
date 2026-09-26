import json
from pathlib import Path

import pytest
from starlette.testclient import TestClient

import agentcore_app
from backend.app.runtime.agentcore_adapter import AgentCoreRuntimeAdapter

SAMPLES = Path(__file__).resolve().parents[2] / "samples"

def load(name):
    return json.loads((SAMPLES / name).read_text(encoding="utf-8"))

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(agentcore_app, "adapter", AgentCoreRuntimeAdapter(str(tmp_path)))
    return TestClient(agentcore_app.app)

def test_ping(client):
    assert client.get("/ping").status_code == 200

def test_complete_package_over_invocations(client):
    result = client.post("/invocations", json=load("study-package-complete.json")).json()
    assert result["status"] == "READY_FOR_HUMAN_REVIEW"
    assert result["human_review_required"] is True

def test_missing_evidence_fails_closed_over_invocations(client):
    result = client.post("/invocations", json=load("study-package-missing-evidence.json")).json()
    assert result["status"] == "NOT_READY_FOR_HUMAN_REVIEW"
    assert "REQ-003" in result["missing_requirement_ids"]

def test_invalid_payload_is_rejected_without_status(client):
    result = client.post("/invocations", json={"study_id": "X"}).json()
    assert result["error"] == "INVALID_STUDY_PACKAGE"
    assert "status" not in result
