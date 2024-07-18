from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import AliasPath, BaseModel, ConfigDict, Field, NonNegativeInt

if TYPE_CHECKING:
    pass


class DeploymentArgs(BaseModel):
    model_config = ConfigDict(extra="allow")


class Deployment(BaseModel):
    name: str
    uuid: str
    description: str | None
    type: str
    status: str
    cooldown_time: NonNegativeInt | None = Field(validation_alias="cooldownTime")
    context_window: NonNegativeInt = Field(validation_alias=AliasPath("model", "maxInputLength"))
    accelerator: str = Field(validation_alias=AliasPath("accelerator", "id"))
    model: str = Field(validation_alias=AliasPath("model", "name"))
    min_replicas: int = Field(validation_alias="minReplicas")
    max_replicas: int = Field(validation_alias="maxReplicas")
    current_replicas: int = Field(validation_alias="currentReplicas")
    scale_up_threshold: int = Field(validation_alias="scaleUpRequestThreshold")
