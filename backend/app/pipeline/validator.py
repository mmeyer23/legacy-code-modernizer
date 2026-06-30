import json

from app.models.migration_models import MigrationContext
from app.models.validation_models import ValidationReport
from app.services.llm_service import analyze_code


def build_validation_prompt(context: MigrationContext, generated_code: str) -> str:
    return f"""
You are a strict code verification engine.

You MUST compare the IR against the generated Python code line-by-line conceptually.

## IR (ground truth specification)
{context.analysis.model_dump_json(indent=2) if context.analysis else "{}"}

## Generated Python code
{generated_code}

---

## REQUIRED CHECKS

### 1. Function Coverage
Ensure every IR function exists in Python.

### 2. Variable Mapping
Ensure all IR variables are represented in Python code (directly or mapped).

### 3. Behavior Preservation
Detect placeholder logic such as:
- "pass"
- "return Unknown"
- dummy arrays like [0] * n

### 4. Hallucinations
Flag any logic not present in IR.

---

## OUTPUT FORMAT (STRICT JSON)

Return a JSON object with the following structure:

Use this exact schema:

passed: boolean
confidence_score: number
strengths: list of strings

issues: list of objects with:
- severity (low, medium, high)
- category (missing_function, mapping_error, placeholder_logic, hallucination)
- message (string)

recommendations: list of strings

Be strict. If placeholders exist, DO NOT give a high confidence score.
Return ONLY JSON.
"""


def validate_translation(context: MigrationContext, generated_code: str) -> ValidationReport:
    prompt = build_validation_prompt(context, generated_code)

    result = analyze_code(prompt)

    try:
        data = json.loads(result)
        return ValidationReport.model_validate(data)

    except Exception as e:
        return ValidationReport(
            passed=False,
            confidence_score=0,
            strengths=[],
            issues=[
                {
                    "severity": "error",
                    "category": "validation_failure",
                    "message": f"Failed to parse validation output: {str(e)}"
                }
            ],
            recommendations=[
                "Fix LLM output format",
                "Ensure model returns strict JSON"
            ]
        )