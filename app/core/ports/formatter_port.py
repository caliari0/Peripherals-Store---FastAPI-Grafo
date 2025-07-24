from abc import ABC, abstractmethod
from typing import Optional


class FormatterPort(ABC):
    """Base class for LLM models."""

    @abstractmethod
    def load(self, path: Optional[str] = None, data: Optional[bytes] = None) -> dict:
        """
        Load data from a file or bytes.
        """
        pass

    @abstractmethod
    def render(self, path: str, input: Optional[dict[str, dict]] = None) -> list[str]:
        """
        Render a template with variables.
        """
        pass
