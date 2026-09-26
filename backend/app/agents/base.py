from abc import ABC, abstractmethod

class BaseAgent(ABC):
    name: str

    @abstractmethod
    def run(self, context: dict) -> dict:
        raise NotImplementedError
