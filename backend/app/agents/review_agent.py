from .base import BaseAgent

class ReviewAgent(BaseAgent):
    name = "review"

    def run(self, context: dict) -> dict:
        requirements = context["requirements"]["requirements"]
        evidence_map = context["evidence_map"]["mapping"]
        quality = context["quality_findings"]

        required = [r for r in requirements if r.get("evidence_required", True)]
        covered = sum(1 for r in required if evidence_map.get(r["id"]))

        return {
            "summary": {
                "required_requirement_count": len(required),
                "requirements_with_evidence": covered,
                "blocking_finding_count": len(quality["blocking"]),
            },
            "unresolved_issues": quality["blocking"] + quality["warnings"],
            "human_review_required": True,
            "decision_boundary": (
                "This workflow assesses evidence-package readiness only. "
                "It does not make clinical, safety, treatment, or regulatory decisions."
            ),
        }
