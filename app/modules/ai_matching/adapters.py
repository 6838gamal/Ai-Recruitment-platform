"""AI Provider Adapter Pattern — pluggable AI providers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from app.config import settings


@dataclass
class MatchAnalysis:
    """Result of an AI matching analysis."""
    score: float           # 0.0 to 100.0
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    missing_skills: List[str]
    provider: str
    model: str


class AIProviderAdapter(ABC):
    """Abstract base class for AI provider adapters."""

    @abstractmethod
    def match_candidate_to_job(
        self,
        candidate_cv_text: str,
        job_description: str,
        job_requirements: Optional[str] = None,
    ) -> MatchAnalysis:
        """Compare candidate CV to job and return match analysis."""
        ...


class OpenAIAdapter(AIProviderAdapter):
    """OpenAI API adapter."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    def match_candidate_to_job(
        self,
        candidate_cv_text: str,
        job_description: str,
        job_requirements: Optional[str] = None,
    ) -> MatchAnalysis:
        """Call OpenAI to analyze candidate-job match."""
        # TODO: Implement OpenAI API call
        raise NotImplementedError("OpenAI adapter not yet configured. Set AI_API_KEY.")


class AnthropicAdapter(AIProviderAdapter):
    """Anthropic Claude adapter."""

    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key
        self.model = model

    def match_candidate_to_job(
        self,
        candidate_cv_text: str,
        job_description: str,
        job_requirements: Optional[str] = None,
    ) -> MatchAnalysis:
        """Call Anthropic to analyze candidate-job match."""
        # TODO: Implement Anthropic API call
        raise NotImplementedError("Anthropic adapter not yet configured. Set AI_API_KEY.")


class LocalLLMAdapter(AIProviderAdapter):
    """Local LLM adapter (Ollama-compatible)."""

    def __init__(self, base_url: str, model: str = "llama3.2"):
        self.base_url = base_url
        self.model = model

    def match_candidate_to_job(
        self,
        candidate_cv_text: str,
        job_description: str,
        job_requirements: Optional[str] = None,
    ) -> MatchAnalysis:
        """Call local LLM to analyze candidate-job match."""
        # TODO: Implement local LLM call
        raise NotImplementedError("Local LLM adapter not yet configured. Set AI_BASE_URL.")


def get_ai_provider() -> AIProviderAdapter:
    """Factory: return the configured AI provider adapter."""
    provider = settings.AI_PROVIDER.lower()

    if provider == "openai":
        return OpenAIAdapter(
            api_key=settings.AI_API_KEY or "",
            model=settings.AI_MODEL,
        )
    elif provider == "anthropic":
        return AnthropicAdapter(
            api_key=settings.AI_API_KEY or "",
            model=settings.AI_MODEL,
        )
    elif provider == "local":
        return LocalLLMAdapter(
            base_url=settings.AI_BASE_URL or "http://localhost:11434",
            model=settings.AI_MODEL,
        )
    else:
        raise ValueError(f"Unknown AI provider: {provider}")
