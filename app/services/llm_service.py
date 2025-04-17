from typing import Dict, Any, Optional
from app.core.agents.llm.factory import LLMFactory
from app.core.agents.llm.interfaces import LLMConfig, LLMResponse
from app.utils.logging import logger

class LLMService:
    """Service class for managing LLM operations."""
    
    def __init__(self):
        self._agents: Dict[str, Any] = {}
        self._active_agent = None

    def initialize_agent(self, provider_type: str) -> None:
        """Initialize a new LLM agent with the specified provider."""
        try:
            agent = LLMFactory.create_agent(provider_type)
            self._agents[provider_type] = agent
            self._active_agent = agent
            logger.info(f"Initialized LLM agent with provider: {provider_type}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM agent: {str(e)}")
            raise

    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> LLMResponse:
        """Send a message to the active LLM agent."""
        if not self._active_agent:
            raise ValueError("No active LLM agent. Please initialize one first.")
        
        try:
            return self._active_agent.chat(message, context)
        except Exception as e:
            logger.error(f"Error in LLM chat: {str(e)}")
            raise

    def set_prompt(self, prompt_id: str) -> None:
        """Set the active prompt template for the active agent."""
        if not self._active_agent:
            raise ValueError("No active LLM agent. Please initialize one first.")
        
        try:
            self._active_agent.set_prompt(prompt_id)
            logger.info(f"Set active prompt to: {prompt_id}")
        except Exception as e:
            logger.error(f"Failed to set prompt: {str(e)}")
            raise

    def update_config(self, config: LLMConfig) -> None:
        """Update the configuration for the active agent."""
        if not self._active_agent:
            raise ValueError("No active LLM agent. Please initialize one first.")
        
        try:
            self._active_agent.update_config(config)
            logger.info("Updated LLM configuration")
        except Exception as e:
            logger.error(f"Failed to update configuration: {str(e)}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the active model."""
        if not self._active_agent:
            raise ValueError("No active LLM agent. Please initialize one first.")
        
        try:
            return self._active_agent.get_model_info()
        except Exception as e:
            logger.error(f"Failed to get model info: {str(e)}")
            raise

    def get_available_providers(self) -> Dict[str, Any]:
        """Get all available LLM providers."""
        return LLMFactory.get_available_providers() 