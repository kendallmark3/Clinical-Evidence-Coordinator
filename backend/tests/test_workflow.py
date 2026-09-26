import json
from pathlib import Path
from backend.app.orchestration.orchestrator import Orchestrator

SAMPLES = Path(__file__).resolve().parents[2] / "samples"

def load(name):
    return json.loads((SAMPLES / name).read_text(encoding="utf-8"))

def test_complete_package_is_ready_for_human_review(tmp_path):
    result = Orchestrator(str(tmp_path)).run(load("study-package-complete.json"))
    assert result["status"] == "READY_FOR_HUMAN_REVIEW"
    assert result["human_review_required"] is True
    assert result["missing_requirement_ids"] == []
    assert result["blocking_findings"] == []

def test_missing_evidence_fails_closed(tmp_path):
    result = Orchestrator(str(tmp_path)).run(load("study-package-missing-evidence.json"))
    assert result["status"] == "NOT_READY_FOR_HUMAN_REVIEW"
    assert "REQ-003" in result["missing_requirement_ids"]
    assert result["blocking_findings"]

def test_unknown_requirement_reference_is_blocking(tmp_path):
    data = load("study-package-complete.json")
    data["evidence_items"][0]["requirement_ids"].append("REQ-999")
    result = Orchestrator(str(tmp_path)).run(data)
    assert result["status"] == "NOT_READY_FOR_HUMAN_REVIEW"
    assert any("REQ-999" in finding for finding in result["blocking_findings"])

def test_duplicate_evidence_id_is_blocking(tmp_path):
    data = load("study-package-complete.json")
    data["evidence_items"][1]["id"] = data["evidence_items"][0]["id"]
    result = Orchestrator(str(tmp_path)).run(data)
    assert result["status"] == "NOT_READY_FOR_HUMAN_REVIEW"
    assert any("Duplicate evidence IDs" in finding for finding in result["blocking_findings"])
