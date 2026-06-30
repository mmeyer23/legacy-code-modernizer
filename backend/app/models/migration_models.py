from typing import Any

from pydantic import BaseModel, Field


class MigrationContext(BaseModel):
    filename: str
    original_source: str
    analysis: dict[str, Any] = Field(default_factory=dict)
