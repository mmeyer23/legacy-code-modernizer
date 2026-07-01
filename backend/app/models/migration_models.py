from pydantic import BaseModel

from app.models.analysis_models import AnalysisIR
from app.models.static_analysis_models import StaticAnalysisReport
from app.models.validation_models import ValidationReport


class MigrationContext(BaseModel):
    filename: str
    original_source: str
    analysis: AnalysisIR | None = None
    analysis_error: str | None = None
    raw_analysis_output: str | None = None
    python_code: str | None = None
    validation: ValidationReport | None = None
    static_analysis: StaticAnalysisReport | None = None