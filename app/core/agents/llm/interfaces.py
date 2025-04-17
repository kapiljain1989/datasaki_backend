from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class LLMConfig(BaseModel):
    """Base configuration for LLM models."""
    model_name: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None

class PromptTemplate(BaseModel):
    """Template for LLM prompts."""
    template: str
    input_variables: List[str]

class LLMResponse(BaseModel):
    """Response from LLM model."""
    content: str
    metadata: Dict[str, Any] = {}

class LLMProvider(ABC):
    """Interface for LLM providers following Interface Segregation Principle."""
    @abstractmethod
    def generate(self, prompt: str, config: LLMConfig) -> LLMResponse:
        """Generate response from the LLM model."""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models from the provider."""
        pass

class PromptManager(ABC):
    """Interface for prompt management following Single Responsibility Principle."""
    @abstractmethod
    def get_prompt(self, prompt_id: str) -> PromptTemplate:
        """Get a prompt template by ID."""
        pass

    @abstractmethod
    def save_prompt(self, prompt_id: str, template: PromptTemplate) -> None:
        """Save a prompt template."""
        pass

    @abstractmethod
    def list_prompts(self) -> List[str]:
        """List all available prompt IDs."""
        pass

class LLMAgent(ABC):
    """Interface for LLM agent following Open/Closed Principle."""
    @abstractmethod
    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> LLMResponse:
        """Process a chat message with optional context."""
        pass

    @abstractmethod
    def set_prompt(self, prompt_id: str) -> None:
        """Set the active prompt template."""
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration."""
        pass 