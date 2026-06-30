from pydantic import BaseModel


class ValidationIssue(BaseModel):
    severity: str  # low | medium | high | critical
    category: str  # missing_function | mapping_error | placeholder_logic | hallucination
    message: str


class CoverageReport(BaseModel):
    functions_total: int
    functions_matched: int
    variables_total: int
    variables_matched: int


class ValidationReport(BaseModel):
    passed: bool
    confidence_score: int  # 0–100

    coverage: CoverageReport

    strengths: list[str]
    issues: list[ValidationIssue]
    recommendations: list[str]