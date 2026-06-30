from pydantic import BaseModel

from app.models.analysis_models import AnalysisIR


class MigrationContext(BaseModel):
    filename: str
    original_source: str
    analysis: AnalysisIR | None = None
    analysis_error: str | None = None
    raw_analysis_output: str | None = None
