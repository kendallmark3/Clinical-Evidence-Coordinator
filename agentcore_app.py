"""
Amazon Bedrock AgentCore Runtime entry point.

This is the only module that imports the AgentCore SDK. It validates the
incoming study package and hands it to the runtime adapter; the domain
workflow in backend/ is unchanged and unaware of AgentCore.

AgentCore Runtime -> this entry point -> AgentCoreRuntimeAdapter -> Orchestrator
"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from pydantic import ValidationError

from backend.app.config import settings
from backend.app.models import StudyPackage
from backend.app.runtime.agentcore_adapter import AgentCoreRuntimeAdapter

app = BedrockAgentCoreApp()
adapter = AgentCoreRuntimeAdapter(settings.artifact_dir)


@app.entrypoint
def invoke(payload, context):
    try:
        package = StudyPackage.model_validate(payload)
    except ValidationError as exc:
        return {
            "error": "INVALID_STUDY_PACKAGE",
            "details": exc.errors(include_url=False, include_context=False, include_input=False),
        }
    return adapter.invoke(package.model_dump())


if __name__ == "__main__":
    app.run()
