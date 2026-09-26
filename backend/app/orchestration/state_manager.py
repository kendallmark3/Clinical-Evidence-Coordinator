from dataclasses import dataclass, field, asdict
from typing import Any
import uuid

@dataclass
class WorkflowState:
    workflow_id: str
    study_id: str
    current_step: str = "created"
    status: str = "RUNNING"
    artifacts: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @classmethod
    def create(cls, study_id: str):
        return cls(workflow_id=str(uuid.uuid4()), study_id=study_id)

    def put(self, key: str, value: Any):
        self.artifacts[key] = value

    def to_dict(self):
        return asdict(self)
