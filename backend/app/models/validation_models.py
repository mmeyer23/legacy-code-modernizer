from pydantic import BaseModel


class SemanticIssue(BaseModel):
    severity: str  # low | medium | high | critical
    category: str  # placeholder_logic | hallucination | mapping_error
    message: str


class SemanticValidation(BaseModel):
    strengths: list[str]
    issues: list[SemanticIssue]
    recommendations: list[str]


class CoverageReport(BaseModel):
    functions_total: int
    functions_matched: int
    variables_total: int
    variables_matched: int


class ValidationReport(BaseModel):
    passed: bool
    confidence_score: int

    coverage: CoverageReport

    strengths: list[str]
    issues: list[SemanticIssue]
    recommendations: list[str]
