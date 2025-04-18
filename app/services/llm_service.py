from typing import Dict, Any, Optional, List
from app.core.agents.llm.factory import LLMFactory
from app.core.agents.llm.interfaces import LLMConfig, LLMResponse
from app.utils.logging import logger
from sqlalchemy.orm import Session
from app.models.llm import LLM
from app.schemas.llm import LLMListResponse, LLMUpdate, LLMChatRequest, LLMChatResponse

class LLMService:
    """Service class for managing LLM operations."""
    
    def __init__(self, db: Session):
        self.db = db
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

    def create_llm(
        self,
        user_id: int,
        name: str,
        provider: str,
        model: str,
        api_key: str,
        config: dict
    ) -> LLMResponse:
        llm = LLM(
            user_id=user_id,
            name=name,
            provider=provider,
            model=model,
            api_key=api_key,
            config=config
        )
        self.db.add(llm)
        self.db.commit()
        self.db.refresh(llm)
        return LLMResponse.from_orm(llm)

    def list_llms(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[int, List[LLMResponse]]:
        query = self.db.query(LLM).filter(LLM.user_id == user_id)
        total = query.count()
        llms = query.offset(skip).limit(limit).all()
        return total, [LLMResponse.from_orm(llm) for llm in llms]

    def get_llm(self, llm_id: int, user_id: int) -> LLMResponse:
        llm = self.db.query(LLM).filter(
            LLM.id == llm_id,
            LLM.user_id == user_id
        ).first()
        if not llm:
            raise ValueError("LLM not found")
        return LLMResponse.from_orm(llm)

    def update_llm(
        self,
        llm_id: int,
        user_id: int,
        name: Optional[str] = None,
        api_key: Optional[str] = None,
        config: Optional[dict] = None
    ) -> LLMResponse:
        llm = self.db.query(LLM).filter(
            LLM.id == llm_id,
            LLM.user_id == user_id
        ).first()
        if not llm:
            raise ValueError("LLM not found")

        if name is not None:
            llm.name = name
        if api_key is not None:
            llm.api_key = api_key
        if config is not None:
            llm.config = config

        self.db.commit()
        self.db.refresh(llm)
        return LLMResponse.from_orm(llm)

    def delete_llm(self, llm_id: int, user_id: int) -> None:
        llm = self.db.query(LLM).filter(
            LLM.id == llm_id,
            LLM.user_id == user_id
        ).first()
        if not llm:
            raise ValueError("LLM not found")
        self.db.delete(llm)
        self.db.commit()

    def chat_with_llm(
        self,
        llm_id: int,
        user_id: int,
        messages: List[dict],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> LLMChatResponse:
        llm = self.db.query(LLM).filter(
            LLM.id == llm_id,
            LLM.user_id == user_id
        ).first()
        if not llm:
            raise ValueError("LLM not found")

        # TODO: Implement actual LLM chat functionality
        # This is a placeholder that should be implemented based on your requirements
        return LLMChatResponse(
            response="Chat functionality to be implemented",
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        ) 