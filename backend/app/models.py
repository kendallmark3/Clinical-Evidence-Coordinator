from typing import List, Literal
from pydantic import BaseModel, Field

EvidenceStatus = Literal["complete", "incomplete", "missing"]

class ProtocolRequirement(BaseModel):
    id: str
    description: str
    evidence_required: bool = True

class EvidenceItem(BaseModel):
    id: str
    evidence_type: str
    source: str
    requirement_ids: List[str] = Field(default_factory=list)
    status: EvidenceStatus = "complete"
    summary: str = ""

class StudyPackage(BaseModel):
    study_id: str
    title: str
    protocol_requirements: List[ProtocolRequirement]
    evidence_items: List[EvidenceItem]

class ReviewResponse(BaseModel):
    workflow_id: str
    study_id: str
    status: Literal["READY_FOR_HUMAN_REVIEW", "NOT_READY_FOR_HUMAN_REVIEW"]
    human_review_required: bool = True
    missing_requirement_ids: List[str]
    blocking_findings: List[str]
    artifacts: dict
