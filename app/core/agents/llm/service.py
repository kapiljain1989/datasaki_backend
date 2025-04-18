from typing import Dict, List, Optional
from app.core.agents.llm.interfaces import LLMConfig, LLMResponse, LLMProvider
from app.core.agents.llm.implementations import OpenAIProvider, GoogleGenAIProvider
from app.utils.logging import logger

class LLMService:
    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {}
        self._active_provider: Optional[LLMProvider] = None
        self._config: Optional[LLMConfig] = None

    def initialize(self, config: LLMConfig) -> None:
        """Initialize the LLM service with the given configuration."""
        self._config = config
        self._providers = {
            "openai": OpenAIProvider(config.api_key, config.model_name),
            "google": GoogleGenAIProvider()
        }
        self._active_provider = self._providers.get(config.provider)
        if not self._active_provider:
            raise ValueError(f"Unsupported provider: {config.provider}")

    def chat(self, messages: List[Dict[str, str]]) -> LLMResponse:
        """Send a chat message to the active LLM provider."""
        if not self._active_provider:
            raise RuntimeError("LLM service not initialized")
        return self._active_provider.chat(
            messages,
            temperature=self._config.temperature,
            max_tokens=self._config.max_tokens
        )

    def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models for each provider."""
        return {
            provider_name: provider.get_available_models()
            for provider_name, provider in self._providers.items()
        }

    def update_config(self, config: LLMConfig) -> None:
        """Update the LLM configuration."""
        self.initialize(config)

    def get_config(self) -> Optional[LLMConfig]:
        """Get the current LLM configuration."""
        return self._config 