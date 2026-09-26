import json
from pathlib import Path

class ArtifactStore:
    def __init__(self, base_dir: str = "artifacts"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write(self, name: str, payload: dict):
        path = self.base_dir / name
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(path)
