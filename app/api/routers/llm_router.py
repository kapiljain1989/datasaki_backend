from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.services.llm_service import LLMService
from app.core.agents.llm.interfaces import LLMConfig, LLMResponse

router = APIRouter(prefix="/llm", tags=["llm"])

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: LLMResponse
    model_info: Dict[str, Any]

@router.post("/initialize/{provider_type}")
async def initialize_agent(provider_type: str, llm_service: LLMService = Depends()):
    """Initialize a new LLM agent with the specified provider."""
    try:
        llm_service.initialize_agent(provider_type)
        return {"message": f"Initialized LLM agent with provider: {provider_type}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/chat")
async def chat(request: ChatRequest, llm_service: LLMService = Depends()) -> ChatResponse:
    """Send a message to the active LLM agent."""
    try:
        response = llm_service.chat(request.message, request.context)
        model_info = llm_service.get_model_info()
        return ChatResponse(response=response, model_info=model_info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/prompt/{prompt_id}")
async def set_prompt(prompt_id: str, llm_service: LLMService = Depends()):
    """Set the active prompt template for the active agent."""
    try:
        llm_service.set_prompt(prompt_id)
        return {"message": f"Set active prompt to: {prompt_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/config")
async def update_config(config: LLMConfig, llm_service: LLMService = Depends()):
    """Update the configuration for the active agent."""
    try:
        llm_service.update_config(config)
        return {"message": "Updated LLM configuration"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/providers")
async def get_providers(llm_service: LLMService = Depends()) -> Dict[str, Any]:
    """Get all available LLM providers."""
    return llm_service.get_available_providers() 