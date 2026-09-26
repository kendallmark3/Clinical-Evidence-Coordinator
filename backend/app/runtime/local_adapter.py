from backend.app.platform.contracts import RuntimeAdapter
from backend.app.orchestration.orchestrator import Orchestrator

class LocalRuntimeAdapter(RuntimeAdapter):
    def __init__(self, artifact_dir: str = "artifacts"):
        self.orchestrator = Orchestrator(artifact_dir)

    def invoke(self, payload: dict) -> dict:
        return self.orchestrator.run(payload)
