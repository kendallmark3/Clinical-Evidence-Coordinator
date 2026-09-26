import json
from pathlib import Path
from backend.app.orchestration.orchestrator import Orchestrator

root = Path(__file__).resolve().parents[1]
for sample in ["study-package-complete.json", "study-package-missing-evidence.json"]:
    payload = json.loads((root / "samples" / sample).read_text(encoding="utf-8"))
    result = Orchestrator(str(root / "artifacts")).run(payload)
    print("=" * 80)
    print(sample)
    print(json.dumps(result, indent=2))
