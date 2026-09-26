from .base import BaseAgent

class RequirementsAgent(BaseAgent):
    name = "requirements"

    def run(self, context: dict) -> dict:
        requirements = context["protocol_requirements"]
        return {
            "requirements": [
                {
                    "id": r["id"],
                    "description": r["description"],
                    "evidence_required": r.get("evidence_required", True),
                }
                for r in requirements
            ],
            "count": len(requirements),
        }
