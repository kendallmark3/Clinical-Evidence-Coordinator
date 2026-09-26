import json
from pathlib import Path
from backend.app.runtime.local_adapter import LocalRuntimeAdapter
from backend.app.runtime.agentcore_adapter import AgentCoreRuntimeAdapter

SAMPLES = Path(__file__).resolve().parents[2] / "samples"

def load(name):
    return json.loads((SAMPLES / name).read_text(encoding="utf-8"))

def test_local_and_agentcore_adapters_preserve_domain_result(tmp_path):
    payload = load("study-package-complete.json")
    local = LocalRuntimeAdapter(str(tmp_path / "local")).invoke(payload)
    cloud = AgentCoreRuntimeAdapter(str(tmp_path / "agentcore")).invoke(payload)

    assert local["status"] == cloud["status"] == "READY_FOR_HUMAN_REVIEW"
    assert local["missing_requirement_ids"] == cloud["missing_requirement_ids"] == []
    assert local["blocking_findings"] == cloud["blocking_findings"] == []
