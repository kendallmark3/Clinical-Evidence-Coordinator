from abc import ABC, abstractmethod
from typing import Any

class ModelProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system: str = "") -> str:
        ...

class RuntimeAdapter(ABC):
    @abstractmethod
    def invoke(self, payload: dict[str, Any]) -> dict[str, Any]:
        ...

class StateRepository(ABC):
    @abstractmethod
    def save(self, workflow_id: str, state: dict[str, Any]) -> None:
        ...

    @abstractmethod
    def load(self, workflow_id: str) -> dict[str, Any] | None:
        ...

class ArtifactRepository(ABC):
    @abstractmethod
    def put_json(self, key: str, payload: dict[str, Any]) -> str:
        ...
