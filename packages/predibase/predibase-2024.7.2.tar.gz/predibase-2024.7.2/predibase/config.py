from __future__ import annotations

from pydantic import BaseModel, Field, NonNegativeInt, PositiveFloat, PositiveInt


class FinetuningConfig(BaseModel):
    base_model: str
    adapter: str = Field(default="lora")
    task: str | None = Field(default=None)
    epochs: PositiveInt | None = Field(default=None)
    learning_rate: PositiveFloat | None = Field(default=None)
    rank: PositiveInt | None = Field(default=None)
    target_modules: list[str] | None = Field(default=None)
    enable_early_stopping: bool = Field(default=True)


class DeploymentConfig(BaseModel):
    base_model: str
    accelerator: str | None = Field(default=None)
    cooldown_time: PositiveInt | None = Field(default=43200)
    hf_token: str | None = Field(default=None)
    min_replicas: NonNegativeInt | None = Field(default=None)
    max_replicas: PositiveInt | None = Field(default=None)
    scale_up_threshold: PositiveInt | None = Field(default=None)
