from typing import Dict, List, Optional
from pydantic import BaseModel

class LLMBase(BaseModel):
    name: str
    provider: str
    model: str
    api_key: str
    config: Dict = {}

class LLMCreate(LLMBase):
    pass

class LLMUpdate(BaseModel):
    name: Optional[str] = None
    api_key: Optional[str] = None
    config: Optional[Dict] = None

class LLMResponse(LLMBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class LLMListResponse(BaseModel):
    total: int
    items: List[LLMResponse]

class LLMChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

class LLMChatResponse(BaseModel):
    response: str
    usage: Dict[str, int] 