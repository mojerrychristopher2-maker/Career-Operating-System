from abc import ABC, abstractmethod


class AIProvider(ABC):

    @abstractmethod
    def ask(self, prompt: str) -> str:
        pass