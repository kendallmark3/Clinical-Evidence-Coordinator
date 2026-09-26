from abc import ABC, abstractmethod

class Provider(ABC):
    name: str

    @abstractmethod
    def generate(self, prompt: str, system: str = "") -> str:
        raise NotImplementedError
