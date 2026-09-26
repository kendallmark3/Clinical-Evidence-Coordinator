from .base import BaseAgent

class EvidenceAgent(BaseAgent):
    name = "evidence"

    def run(self, context: dict) -> dict:
        requirements = context["requirements"]["requirements"]
        evidence_items = context["evidence_items"]

        mapping = {}
        for req in requirements:
            rid = req["id"]
            matches = [
                {
                    "evidence_id": e["id"],
                    "source": e["source"],
                    "status": e["status"],
                    "evidence_type": e["evidence_type"],
                }
                for e in evidence_items
                if rid in e.get("requirement_ids", [])
            ]
            mapping[rid] = matches

        return {"mapping": mapping}
