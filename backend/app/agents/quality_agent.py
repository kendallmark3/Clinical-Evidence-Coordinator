from collections import Counter
from .base import BaseAgent

class QualityAgent(BaseAgent):
    name = "quality"

    def run(self, context: dict) -> dict:
        requirements = context["requirements"]["requirements"]
        evidence_items = context["evidence_items"]
        evidence_map = context["evidence_map"]["mapping"]

        known_requirement_ids = {r["id"] for r in requirements}
        blocking = []
        warnings = []

        ids = [e["id"] for e in evidence_items]
        duplicates = sorted([eid for eid, count in Counter(ids).items() if count > 1])
        if duplicates:
            blocking.append(f"Duplicate evidence IDs: {', '.join(duplicates)}")

        for e in evidence_items:
            unknown = sorted(set(e.get("requirement_ids", [])) - known_requirement_ids)
            if unknown:
                blocking.append(
                    f"Evidence {e['id']} references unknown requirement(s): {', '.join(unknown)}"
                )

        for req in requirements:
            if not req.get("evidence_required", True):
                continue
            mapped = evidence_map.get(req["id"], [])
            if not mapped:
                blocking.append(f"Required evidence missing for {req['id']}")
                continue
            usable = [m for m in mapped if m["status"] == "complete"]
            if not usable:
                blocking.append(f"No complete evidence available for {req['id']}")

        return {"blocking": blocking, "warnings": warnings}
