from pydantic import BaseModel


class ValidationIssue(BaseModel):
    severity: str
    category: str
    message: str


class ValidationReport(BaseModel):
    passed: bool
    confidence_score: int

    strengths: list[str]

    issues: list[ValidationIssue]

    recommendations: list[str]