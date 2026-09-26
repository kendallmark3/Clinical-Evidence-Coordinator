from backend.app.agents.requirements_agent import RequirementsAgent
from backend.app.agents.evidence_agent import EvidenceAgent
from backend.app.agents.quality_agent import QualityAgent
from backend.app.agents.review_agent import ReviewAgent
from backend.app.agents.document_intake_agent import DocumentIntakeAgent
from backend.app.providers.base import Provider
from backend.app.orchestration.state_manager import WorkflowState
from backend.app.orchestration.artifact_store import ArtifactStore
from backend.app.validation.validator import validate

class Orchestrator:
    def __init__(self, artifact_dir: str = "artifacts", provider: Provider | None = None):
        self.provider = provider
        self.requirements_agent = RequirementsAgent()
        self.evidence_agent = EvidenceAgent()
        self.quality_agent = QualityAgent()
        self.review_agent = ReviewAgent()
        self.store = ArtifactStore(artifact_dir)

    def run_documents(self, study_id: str, title: str,
                      protocol_requirements: list[dict], documents: list[dict]) -> dict:
        """Classify uploaded documents into evidence items, then run the standard workflow."""
        if self.provider is None:
            raise ValueError("A model provider is required to classify documents.")

        intake = DocumentIntakeAgent(self.provider).run({
            "requirements": protocol_requirements,
            "documents": documents,
        })
        self.store.write("document-intake.json", intake)

        result = self.run({
            "study_id": study_id,
            "title": title,
            "protocol_requirements": protocol_requirements,
            "evidence_items": intake["evidence_items"],
        })
        result["artifacts"] = {"document_intake": intake, **result["artifacts"]}
        return result

    def run(self, study: dict) -> dict:
        state = WorkflowState.create(study_id=study["study_id"])

        state.current_step = "normalize-requirements"
        requirements = self.requirements_agent.run({
            "protocol_requirements": study["protocol_requirements"]
        })
        state.put("requirements", requirements)
        self.store.write("requirements.json", requirements)

        state.current_step = "map-evidence"
        evidence_map = self.evidence_agent.run({
            "requirements": requirements,
            "evidence_items": study["evidence_items"],
        })
        state.put("evidence_map", evidence_map)
        self.store.write("evidence-map.json", evidence_map)

        state.current_step = "inspect-quality"
        quality = self.quality_agent.run({
            "requirements": requirements,
            "evidence_items": study["evidence_items"],
            "evidence_map": evidence_map,
        })
        state.put("quality_findings", quality)
        self.store.write("quality-findings.json", quality)

        state.current_step = "prepare-human-review"
        review = self.review_agent.run({
            "requirements": requirements,
            "evidence_map": evidence_map,
            "quality_findings": quality,
        })
        state.put("review_summary", review)
        self.store.write("review-summary.json", review)

        state.current_step = "deterministic-validation"
        validation = validate(requirements, evidence_map, quality)
        state.put("validation_result", validation)
        self.store.write("validation-result.json", validation)

        state.status = validation["status"]
        state.current_step = "complete"
        self.store.write("workflow-state.json", state.to_dict())

        return {
            "workflow_id": state.workflow_id,
            "study_id": state.study_id,
            **validation,
            "artifacts": state.artifacts,
        }
