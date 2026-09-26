"""
Amazon Bedrock AgentCore adapter boundary.

Use the current AgentCore CLI to scaffold the supported runtime entry point,
then call the existing domain orchestrator from that entry point.

Dependency direction:

AgentCore entry point -> this adapter -> Orchestrator

NOT:

domain agents -> AgentCore SDK
"""

from backend.app.platform.contracts import RuntimeAdapter
from backend.app.orchestration.orchestrator import Orchestrator

class AgentCoreRuntimeAdapter(RuntimeAdapter):
    def __init__(self, artifact_dir: str = "/tmp/artifacts"):
        self.orchestrator = Orchestrator(artifact_dir)

    def invoke(self, payload: dict) -> dict:
        return self.orchestrator.run(payload)
