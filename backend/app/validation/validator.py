def validate(requirements: dict, evidence_map: dict, quality_findings: dict) -> dict:
    missing = []
    mapping = evidence_map["mapping"]

    for req in requirements["requirements"]:
        if not req.get("evidence_required", True):
            continue

        matches = mapping.get(req["id"], [])
        complete = [m for m in matches if m.get("status") == "complete"]
        if not complete:
            missing.append(req["id"])

    blocking = list(quality_findings.get("blocking", []))
    ready = not missing and not blocking

    return {
        "status": "READY_FOR_HUMAN_REVIEW" if ready else "NOT_READY_FOR_HUMAN_REVIEW",
        "human_review_required": True,
        "missing_requirement_ids": sorted(set(missing)),
        "blocking_findings": blocking,
        "rules": {
            "all_required_requirements_have_complete_evidence": not missing,
            "no_blocking_quality_findings": not blocking,
            "human_review_required": True,
        },
    }
