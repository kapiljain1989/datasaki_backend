from typing import Any, Dict, List, Optional
from langchain_core.prompts import PromptTemplate as LangChainPromptTemplate
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.agents.llm.interfaces import (
    LLMConfig, PromptTemplate, LLMResponse, LLMProvider, 
    PromptManager, LLMAgent
)
from app.utils.logging import logger
import os

class LangChainPromptManager(PromptManager):
    """Concrete implementation of PromptManager using LangChain."""
    def __init__(self):
        self._prompts: Dict[str, PromptTemplate] = {}
        self._load_default_prompts()

    def _load_default_prompts(self):
        """Load default prompt templates."""
        self._prompts["default"] = PromptTemplate(
            template="You are a helpful AI assistant. {message}",
            input_variables=["message"]
        )
        self._prompts["analyst"] = PromptTemplate(
            template="You are a data analyst. Analyze the following: {message}",
            input_variables=["message"]
        )
        self._prompts["coder"] = PromptTemplate(
            template="You are a coding assistant. Help with: {message}",
            input_variables=["message"]
        )

    def get_prompt(self, prompt_id: str) -> PromptTemplate:
        if prompt_id not in self._prompts:
            raise ValueError(f"Prompt template {prompt_id} not found")
        return self._prompts[prompt_id]

    def save_prompt(self, prompt_id: str, template: PromptTemplate) -> None:
        self._prompts[prompt_id] = template

    def list_prompts(self) -> List[str]:
        return list(self._prompts.keys())

class OpenAIProvider(LLMProvider):
    """Concrete implementation for OpenAI models."""
    def __init__(self):
        self._client = None

    def _get_client(self, config: LLMConfig) -> BaseChatModel:
        if not self._client:
            self._client = ChatOpenAI(
                model_name=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                api_key=config.api_key or os.getenv("OPENAI_API_KEY"),
                base_url=config.api_base
            )
        return self._client

    def generate(self, prompt: str, config: LLMConfig) -> LLMResponse:
        try:
            client = self._get_client(config)
            response = client.invoke(prompt)
            return LLMResponse(
                content=response.content,
                metadata={
                    "model": config.model_name,
                    "provider": "openai"
                }
            )
        except Exception as e:
            logger.error(f"Error generating response from OpenAI: {str(e)}")
            raise

    def get_available_models(self) -> List[str]:
        return [
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-3.5-turbo"
        ]

class AnthropicProvider(LLMProvider):
    """Concrete implementation for Anthropic models."""
    def __init__(self):
        self._client = None

    def _get_client(self, config: LLMConfig) -> BaseChatModel:
        if not self._client:
            self._client = ChatAnthropic(
                model_name=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                api_key=config.api_key or os.getenv("ANTHROPIC_API_KEY")
            )
        return self._client

    def generate(self, prompt: str, config: LLMConfig) -> LLMResponse:
        try:
            client = self._get_client(config)
            response = client.invoke(prompt)
            return LLMResponse(
                content=response.content,
                metadata={
                    "model": config.model_name,
                    "provider": "anthropic"
                }
            )
        except Exception as e:
            logger.error(f"Error generating response from Anthropic: {str(e)}")
            raise

    def get_available_models(self) -> List[str]:
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-2.1"
        ]

class GoogleGenAIProvider(LLMProvider):
    """Concrete implementation for Google Generative AI models."""
    def __init__(self):
        self._client = None

    def _get_client(self, config: LLMConfig) -> BaseChatModel:
        if not self._client:
            self._client = ChatGoogleGenerativeAI(
                model=config.model_name,
                temperature=config.temperature,
                max_output_tokens=config.max_tokens,
                google_api_key=config.api_key or os.getenv("GOOGLE_API_KEY")
            )
        return self._client

    def generate(self, prompt: str, config: LLMConfig) -> LLMResponse:
        try:
            client = self._get_client(config)
            response = client.invoke(prompt)
            return LLMResponse(
                content=response.content,
                metadata={
                    "model": config.model_name,
                    "provider": "google"
                }
            )
        except Exception as e:
            logger.error(f"Error generating response from Google GenAI: {str(e)}")
            raise

    def get_available_models(self) -> List[str]:
        return [
            "gemini-pro",
            "gemini-1.5-pro"
        ]

class LLMAgentImpl(LLMAgent):
    """Concrete implementation of LLMAgent following Dependency Inversion Principle."""
    def __init__(self, provider: LLMProvider, prompt_manager: PromptManager):
        self._provider = provider
        self._prompt_manager = prompt_manager
        self._active_prompt_id = "default"
        self._config = LLMConfig(
            model_name=provider.get_available_models()[0],
            temperature=0.7
        )

    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> LLMResponse:
        try:
            # Get the active prompt template
            prompt_template = self._prompt_manager.get_prompt(self._active_prompt_id)
            
            # Format the prompt with the message and context
            formatted_prompt = prompt_template.template.format(
                message=message,
                **(context or {})
            )
            
            # Generate response using the provider
            return self._provider.generate(formatted_prompt, self._config)
            
        except Exception as e:
            logger.error(f"Error in LLM chat: {str(e)}")
            raise

    def set_prompt(self, prompt_id: str) -> None:
        if prompt_id not in self._prompt_manager.list_prompts():
            raise ValueError(f"Prompt template {prompt_id} not found")
        self._active_prompt_id = prompt_id

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model": self._config.model_name,
            "temperature": self._config.temperature,
            "max_tokens": self._config.max_tokens,
            "active_prompt": self._active_prompt_id,
            "available_models": self._provider.get_available_models()
        }

    def update_config(self, config: LLMConfig) -> None:
        """Update the LLM configuration."""
        self._config = config 