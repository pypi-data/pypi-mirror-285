from typing import Dict, Tuple, Type

import pydantic

PYDANTIC_V2 = hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2.")

if PYDANTIC_V2:
    from pydantic.v1 import BaseModel
else:
    from pydantic import BaseModel

from scale_egp.sdk.enums import ModelType
from scale_egp.sdk.types.models import (
    AgentRequest,
    AgentResponse,
    ChatCompletionRequest,
    ChatCompletionResponse,
    CompletionRequest,
    CompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    RerankingRequest,
    RerankingResponse,
)

MODEL_SCHEMAS: Dict[ModelType, Tuple[Type[BaseModel], Type[BaseModel]]] = {
    ModelType.COMPLETION: (CompletionRequest, CompletionResponse),
    ModelType.CHAT_COMPLETION: (ChatCompletionRequest, ChatCompletionResponse),
    ModelType.AGENT: (AgentRequest, AgentResponse),
    ModelType.RERANKING: (RerankingRequest, RerankingResponse),
    ModelType.EMBEDDING: (EmbeddingRequest, EmbeddingResponse),
}
