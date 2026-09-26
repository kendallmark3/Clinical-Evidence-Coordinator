import json
import re

from .base import Provider

# Words too generic to identify a requirement on their own.
STOPWORDS = {
    "the", "and", "for", "are", "is", "a", "an", "of", "study", "document",
    "present", "record", "records", "results", "summary",
}
INCOMPLETE_MARKERS = ("draft", "pending", "partial")

class MockProvider(Provider):
    """Offline stand-in for a model. Not AI.

    For document-intake prompts (requirements JSON inside <requirements> and
    text inside <document>) it matches a document to a requirement when every
    distinctive word of the requirement appears in the text, and marks the
    document incomplete if it mentions draft/pending/partial. Anything else
    gets a fixed response.
    """

    name = "mock"

    def generate(self, prompt: str, system: str = "") -> str:
        reqs = re.search(r"<requirements>(.*?)</requirements>", prompt, re.S)
        doc = re.search(r"<document>(.*?)</document>", prompt, re.S)
        if not (reqs and doc):
            return "MOCK_PROVIDER_RESPONSE"

        text = doc.group(1).lower()
        words = set(re.findall(r"[a-z]+", text))
        matched = []
        for req in json.loads(reqs.group(1)):
            keywords = {w for w in re.findall(r"[a-z]+", req["description"].lower())
                        if w not in STOPWORDS and len(w) > 2}
            if keywords and keywords <= words:
                matched.append(req["id"])

        incomplete = any(marker in text for marker in INCOMPLETE_MARKERS)
        return json.dumps({
            "requirement_ids": matched,
            "evidence_type": "unclassified",
            "status": "incomplete" if incomplete else "complete",
            "summary": "Classified by keyword matching (mock provider, not AI).",
            "rationale": f"Keyword match on {', '.join(matched) or 'no requirements'}; "
                         f"{'draft/pending marker found' if incomplete else 'no draft/pending marker'}.",
        })
