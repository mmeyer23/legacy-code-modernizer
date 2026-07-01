import json

from app.models.migration_models import MigrationContext
from app.models.static_analysis_models import StaticAnalysisReport
from app.models.validation_models import (
    SemanticValidation,
    ValidationReport,
    CoverageReport,
)
from app.services.llm_service import analyze_code


def build_validation_prompt(
    context: MigrationContext,
    generated_code: str,
    static_report: StaticAnalysisReport,
) -> str:
    return f"""
You are a software migration validation engine.

Your job is to evaluate the semantic correctness of generated Python code against the provided Intermediate Representation (IR).

The deterministic structure of the code (function existence, variable existence, syntax, and coverage) has ALREADY been validated by the application.

DO NOT evaluate structural coverage.

Your ONLY responsibilities are:

1. Detect placeholder implementations.
2. Detect hallucinated behavior.
3. Detect incorrect mappings from the IR.
4. Determine whether the generated code preserves the intent of the original program.

--------------------------------------------------
INTERMEDIATE REPRESENTATION (Ground Truth)
--------------------------------------------------

{context.analysis.model_dump_json(indent=2) if context.analysis else "{}"}

--------------------------------------------------
Generated Python Code
--------------------------------------------------

{generated_code}

--------------------------------------------------
STATIC ANALYSIS (Deterministic)
--------------------------------------------------

{json.dumps(static_report.model_dump(), indent=2)}

--------------------------------------------------
VALIDATION RULES
--------------------------------------------------

Placeholder Logic:
Flag implementations that are clearly unfinished, including:
- pass
- ...
- return "Unknown"
- return None
- TODO comments
- placeholder comments indicating missing implementation

Hallucinations:
Flag code that invents:
- functions
- classes
- business logic
- mappings
- behavior
that cannot be inferred from the IR.

Incorrect Mapping:
Flag implementations that contradict the IR.

Behavior Preservation:
Determine whether the generated code preserves the intent of the original program.

When multiple functions violate the same rule,
create one issue per function.

Do NOT combine multiple violations into a single issue.

--------------------------------------------------
Issue Categories (STRICT ENUM)
--------------------------------------------------

Use ONLY:

- placeholder_logic
- hallucination
- mapping_error

--------------------------------------------------
OUTPUT FORMAT
--------------------------------------------------

Return ONLY valid JSON.

{{
  "strengths": [
    "string"
  ],
  "issues": [
    {{
      "severity": "low | medium | high | critical",
      "category": "placeholder_logic | hallucination | mapping_error",
      "message": "string"
    }}
  ],
  "recommendations": [
    "string"
  ]
}}

Return JSON only.
"""
    

def validate_translation(
    context: MigrationContext,
    generated_code: str,
    static_report: StaticAnalysisReport,
) -> ValidationReport:

    if context.analysis is None:
        return ValidationReport(
            passed=False,
            confidence_score=0,
            coverage=CoverageReport(
                functions_total=0,
                functions_matched=0,
                variables_total=0,
                variables_matched=0,
            ),
            strengths=[],
            issues=[],
            recommendations=[
                "Fix analysis parsing before validating translation."
            ],
        )

    prompt = build_validation_prompt(
        context,
        generated_code,
        static_report,
    )

    result = analyze_code(prompt)

    try:
        data = json.loads(result)

        semantic_validation = SemanticValidation.model_validate(data)

        score = 100

        for issue in semantic_validation.issues:
            if issue.severity == "critical":
                score -= 30
            elif issue.severity == "high":
                score -= 20
            elif issue.severity == "medium":
                score -= 10
            elif issue.severity == "low":
                score -= 5

        if static_report.functions_matched != static_report.functions_total:
            score -= 20

        if static_report.variables_matched != static_report.variables_total:
            score -= 10

        score = max(0, min(score, 100))

        has_serious_issue = any(
            issue.severity in {"high", "critical"}
            for issue in semantic_validation.issues
        )

        passed = (
            score >= 80
            and not has_serious_issue
            and static_report.functions_matched == static_report.functions_total
            and static_report.variables_matched == static_report.variables_total
        )

        return ValidationReport(
            passed=passed,
            confidence_score=score,
            coverage=CoverageReport(
                functions_total=static_report.functions_total,
                functions_matched=static_report.functions_matched,
                variables_total=static_report.variables_total,
                variables_matched=static_report.variables_matched,
            ),
            strengths=semantic_validation.strengths,
            issues=semantic_validation.issues,
            recommendations=semantic_validation.recommendations,
        )

    except Exception as e:
        return ValidationReport(
            passed=False,
            confidence_score=0,
            coverage=CoverageReport(
                functions_total=static_report.functions_total,
                functions_matched=static_report.functions_matched,
                variables_total=static_report.variables_total,
                variables_matched=static_report.variables_matched,
            ),
            strengths=[],
            issues=[],
            recommendations=[
                f"Failed to parse validation output: {str(e)}"
            ],
        )