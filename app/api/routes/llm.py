from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services.llm_service import LLMService
from app.core.agents.llm.interfaces import LLMConfig, LLMResponse
from app.models.user import User
from app.schemas.llm import (
    LLMListResponse,
    LLMUpdate,
    LLMChatRequest,
    LLMChatResponse
)
from app.dependencies import get_db, get_current_user, validate_token
from app.utils.logging import logger

router = APIRouter(dependencies=[Depends(validate_token)])

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: LLMResponse
    model_info: Dict[str, Any]

class MessageResponse(BaseModel):
    message: str

@router.post("/initialize/{provider_type}", response_model=MessageResponse)
async def initialize_agent(
    provider_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Initialize a new LLM agent with the specified provider."""
    try:
        logger.info(f"Initializing LLM agent for user {current_user.id} with provider {provider_type}")
        service = LLMService(db)
        service.initialize_agent(provider_type)
        return MessageResponse(message=f"Initialized LLM agent with provider: {provider_type}")
    except Exception as e:
        logger.error(f"Failed to initialize LLM agent: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Send a message to the active LLM agent."""
    try:
        logger.info(f"Processing chat request for user {current_user.id}")
        service = LLMService(db)
        response = service.chat(request.message, request.context)
        model_info = service.get_model_info()
        return ChatResponse(response=response, model_info=model_info)
    except Exception as e:
        logger.error(f"Chat request failed: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/prompt/{prompt_id}", response_model=MessageResponse)
async def set_prompt(
    prompt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Set the active prompt template for the active agent."""
    try:
        logger.info(f"Setting prompt {prompt_id} for user {current_user.id}")
        service = LLMService(db)
        service.set_prompt(prompt_id)
        return MessageResponse(message=f"Set active prompt to: {prompt_id}")
    except Exception as e:
        logger.error(f"Failed to set prompt: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/config", response_model=MessageResponse)
async def update_config(
    config: LLMConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Update the configuration for the active agent."""
    try:
        logger.info(f"Updating LLM config for user {current_user.id}")
        service = LLMService(db)
        service.update_config(config)
        return MessageResponse(message="Updated LLM configuration")
    except Exception as e:
        logger.error(f"Failed to update config: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/providers")
async def get_providers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
) -> Dict[str, Any]:
    """Get all available LLM providers."""
    try:
        logger.info(f"Getting providers for user {current_user.id}")
        service = LLMService(db)
        return service.get_available_providers()
    except Exception as e:
        logger.error(f"Failed to get providers: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=LLMResponse)
async def create_llm(
    llm_config: LLMConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Create a new LLM configuration for the current user."""
    try:
        logger.info(f"Creating LLM config for user {current_user.id}")
        service = LLMService(db)
        result = service.create_llm(
            user_id=current_user.id,
            name=llm_config.name,
            provider=llm_config.provider,
            model=llm_config.model,
            api_key=llm_config.api_key,
            config=llm_config.config
        )
        return result
    except Exception as e:
        logger.error(f"Failed to create LLM: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=LLMListResponse)
async def list_llms(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """List LLM configurations for the current user."""
    try:
        logger.info(f"Listing LLMs for user {current_user.id}")
        service = LLMService(db)
        llms, total = service.list_llms(
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        return LLMListResponse(total=total, items=llms)
    except Exception as e:
        logger.error(f"Failed to list LLMs: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{llm_id}", response_model=LLMResponse)
async def get_llm(
    llm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Get LLM configuration for the current user."""
    try:
        logger.info(f"Getting LLM {llm_id} for user {current_user.id}")
        service = LLMService(db)
        return service.get_llm(llm_id, user_id=current_user.id)
    except Exception as e:
        logger.error(f"Failed to get LLM: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{llm_id}", response_model=LLMResponse)
async def update_llm(
    llm_id: int,
    llm_update: LLMUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Update LLM configuration for the current user."""
    try:
        logger.info(f"Updating LLM {llm_id} for user {current_user.id}")
        service = LLMService(db)
        result = service.update_llm(
            llm_id=llm_id,
            user_id=current_user.id,
            name=llm_update.name,
            api_key=llm_update.api_key,
            config=llm_update.config
        )
        return result
    except Exception as e:
        logger.error(f"Failed to update LLM: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{llm_id}", response_model=MessageResponse)
async def delete_llm(
    llm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Delete LLM configuration for the current user."""
    try:
        logger.info(f"Deleting LLM {llm_id} for user {current_user.id}")
        service = LLMService(db)
        service.delete_llm(llm_id, user_id=current_user.id)
        return MessageResponse(message="LLM configuration deleted successfully")
    except Exception as e:
        logger.error(f"Failed to delete LLM: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{llm_id}/chat", response_model=LLMChatResponse)
async def chat_with_llm(
    llm_id: int,
    chat_request: LLMChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Chat with LLM for the current user."""
    try:
        logger.info(f"Chatting with LLM {llm_id} for user {current_user.id}")
        service = LLMService(db)
        result = service.chat_with_llm(
            llm_id=llm_id,
            user_id=current_user.id,
            messages=chat_request.messages,
            temperature=chat_request.temperature,
            max_tokens=chat_request.max_tokens
        )
        return result
    except Exception as e:
        logger.error(f"Failed to chat with LLM: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e)) 