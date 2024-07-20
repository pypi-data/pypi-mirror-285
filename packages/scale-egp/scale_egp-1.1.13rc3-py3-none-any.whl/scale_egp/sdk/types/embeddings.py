from enum import Enum
from typing import Literal, Union

import pydantic

PYDANTIC_V2 = hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2.")

if PYDANTIC_V2:
    from pydantic.v1 import Field
else:
    from pydantic import Field

from scale_egp.utils.model_utils import BaseModel, RootModel
from scale_egp.sdk.enums import EmbeddingModelName, EmbeddingConfigType



class EmbeddingConfigBase(BaseModel):
    type: Literal[EmbeddingConfigType.BASE] = Field(
        EmbeddingConfigType.BASE, description="The type of the embedding configuration."
    )
    embedding_model: EmbeddingModelName = Field(
        description="The name of the base embedding model to use. To use custom models, change to type 'models'."
    )


class EmbeddingConfigModelsAPI(BaseModel):
    type: Literal[EmbeddingConfigType.MODELS_API] = Field(
        EmbeddingConfigType.MODELS_API, description="The type of the embedding configuration."
    )
    model_deployment_id: str = Field(
        description="The ID of the deployment of the created model in the Models API V3."
    )


class EmbeddingConfig(RootModel):
    __root__: Union[EmbeddingConfigModelsAPI, EmbeddingConfigBase]