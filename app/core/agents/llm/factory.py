from typing import Dict, Optional
from app.core.agents.llm.interfaces import LLMProvider, LLMConfig
from app.core.agents.llm.implementations import OpenAIProvider, GoogleGenAIProvider
from app.utils.logging import logger

class LLMFactory:
    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {}
        self._active_provider: Optional[LLMProvider] = None
        self._config: Optional[LLMConfig] = None

    def initialize(self, config: LLMConfig) -> None:
        """Initialize the LLM factory with the given configuration."""
        self._config = config
        self._providers = {
            "openai": OpenAIProvider(config.api_key, config.model_name),
            "google": GoogleGenAIProvider()
        }
        self._active_provider = self._providers.get(config.provider)
        if not self._active_provider:
            raise ValueError(f"Unsupported provider: {config.provider}")

    def get_provider(self) -> LLMProvider:
        """Get the active LLM provider."""
        if not self._active_provider:
            raise RuntimeError("LLM factory not initialized")
        return self._active_provider

    def get_available_providers(self) -> Dict[str, LLMProvider]:
        """Get all available providers."""
        return self._providers

    def update_config(self, config: LLMConfig) -> None:
        """Update the LLM configuration."""
        self.initialize(config)

    def get_config(self) -> Optional[LLMConfig]:
        """Get the current LLM configuration."""
        return self._config 