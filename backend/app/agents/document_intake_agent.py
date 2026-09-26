import json
import re
from pathlib import Path

from backend.app.providers.base import Provider
from .base import BaseAgent

PROMPT_PATH = Path(__file__).resolve().parents[3] / "prompts" / "document_intake.md"
ALLOWED_STATUS = {"complete", "incomplete"}

class DocumentIntakeAgent(BaseAgent):
    """Turns uploaded documents into proposed evidence items.

    The provider proposes; this agent checks the shape of every answer and
    fails closed (no requirements, status incomplete) when it cannot trust it.
    The deterministic validator still makes the final readiness call.
    """

    name = "document_intake"

    def __init__(self, provider: Provider):
        self.provider = provider
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    def run(self, context: dict) -> dict:
        requirements = context["requirements"]
        evidence_items = []
        classifications = []

        for index, doc in enumerate(context["documents"], start=1):
            evidence_id = f"DOC-{index:03d}"
            proposal, error = self._classify(requirements, doc["text"])
            evidence_items.append({
                "id": evidence_id,
                "evidence_type": proposal["evidence_type"],
                "source": doc["filename"],
                "requirement_ids": proposal["requirement_ids"],
                "status": proposal["status"],
                "summary": proposal["summary"],
            })
            classifications.append({
                "evidence_id": evidence_id,
                "filename": doc["filename"],
                "classified_by": self.provider.name,
                "rationale": proposal["rationale"],
                "error": error,
            })

        return {"evidence_items": evidence_items, "classifications": classifications}

    def _classify(self, requirements: list[dict], text: str) -> tuple[dict, str | None]:
        if not text.strip():
            return _fail_closed("No extractable text (the PDF may be scanned or empty).")

        prompt = (
            "<requirements>"
            + json.dumps([{"id": r["id"], "description": r["description"]} for r in requirements])
            + "</requirements>\n<document>\n" + text + "\n</document>"
        )
        try:
            raw = self.provider.generate(prompt, system=self.system_prompt)
        except Exception as exc:
            return _fail_closed(f"Provider call failed: {exc}")
        return _parse(raw)

def _parse(raw: str) -> tuple[dict, str | None]:
    match = re.search(r"\{.*\}", raw, re.S)
    try:
        data = json.loads(match.group(0)) if match else None
    except json.JSONDecodeError:
        data = None
    if not isinstance(data, dict):
        return _fail_closed("Provider response was not a JSON object.")

    ids = data.get("requirement_ids")
    if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
        return _fail_closed("Provider response had invalid requirement_ids.")
    status = data.get("status")
    if status not in ALLOWED_STATUS:
        return _fail_closed(f"Provider response had invalid status {status!r}.")

    return {
        "requirement_ids": ids,
        "evidence_type": str(data.get("evidence_type") or "unclassified"),
        "status": status,
        "summary": str(data.get("summary") or ""),
        "rationale": str(data.get("rationale") or ""),
    }, None

def _fail_closed(reason: str) -> tuple[dict, str]:
    return {
        "requirement_ids": [],
        "evidence_type": "unclassified",
        "status": "incomplete",
        "summary": "",
        "rationale": reason,
    }, reason
