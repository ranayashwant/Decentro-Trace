from abc import ABC, abstractmethod
from typing import Any
from app.schemas.investigation import InvestigationResult


class AIProvider(ABC):
    """
    Abstract interface for AI investigation provider.
    Ensures strict architectural boundary:
    The application depends on this interface, not a specific LLM vendor SDK.
    """

    @abstractmethod
    async def investigate(self, trace_context: dict[str, Any]) -> InvestigationResult:
        """
        Takes structured trace context (deterministic facts) and returns structured analysis.
        """
        pass
