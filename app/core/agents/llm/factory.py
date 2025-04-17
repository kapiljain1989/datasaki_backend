from typing import Dict, Type
from app.core.agents.llm.interfaces import LLMProvider, LLMAgent
from app.core.agents.llm.implementations import (
    OpenAIProvider,
    AnthropicProvider,
    GoogleGenAIProvider,
    LLMAgentImpl,
    LangChainPromptManager
)

class LLMFactory:
    """Factory class for creating LLM agents and providers."""
    
    _providers: Dict[str, Type[LLMProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "google": GoogleGenAIProvider
    }

    @classmethod
    def create_provider(cls, provider_type: str) -> LLMProvider:
        """Create a new LLM provider instance."""
        if provider_type not in cls._providers:
            raise ValueError(f"Unknown provider type: {provider_type}")
        return cls._providers[provider_type]()

    @classmethod
    def create_agent(cls, provider_type: str) -> LLMAgent:
        """Create a new LLM agent with the specified provider."""
        provider = cls.create_provider(provider_type)
        prompt_manager = LangChainPromptManager()
        return LLMAgentImpl(provider, prompt_manager)

    @classmethod
    def get_available_providers(cls) -> Dict[str, Type[LLMProvider]]:
        """Get all available provider types."""
        return cls._providers.copy() 