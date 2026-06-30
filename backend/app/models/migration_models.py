from pydantic import BaseModel
from typing import Any


class MigrationContext(BaseModel):
    filename: str
    original_source: str
    analysis: dict[str, Any]