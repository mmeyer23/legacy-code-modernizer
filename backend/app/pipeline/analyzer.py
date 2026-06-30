from pydantic import ValidationError
from app.models.analysis_models import AnalysisIR
from app.models.migration_models import MigrationContext
from app.services.llm_service import analyze_code


def build_analysis_prompt(fortran_code: str) -> str:
    return f"""
You are an expert software engineer specializing in legacy system modernization.

Analyze the following Fortran code and return ONLY valid JSON.

DO NOT include markdown, explanations, or text outside JSON.

Return exactly this structure:

{{
  "summary": "string",

  "inputs": [
    "string"
  ],

  "outputs": [
    "string"
  ],

  "variables": [
    {{
      "name": "string",
      "type": "string",
      "purpose": "string"
    }}
  ],

  "functions": [
    {{
      "name": "string",
      "purpose": "string",
      "parameters": [
        "string"
      ],
      "returns": "string",
      "calls": [
        "string"
      ]
    }}
  ],

  "data_flow": [
    "string"
  ],

  "migration_challenges": [
    "string"
  ]
}}

Rules:
- Return ONLY valid JSON.
- Every field in the schema is required.
- Never omit a field.
- Use [] for empty arrays.
- Use "Unknown" when a string value cannot be determined.
- Do not invent functionality that is not present.
- Infer conservatively.
- The output will be parsed by another software component.

Fortran Code:
----------------
{fortran_code}
----------------
"""


def analyze_fortran_code(context: MigrationContext) -> MigrationContext:
    prompt = build_analysis_prompt(context.original_source)
    result = analyze_code(prompt)

    try:
        analysis = AnalysisIR.model_validate_json(result)
    except ValidationError as e:
        analysis = {
        "error": "Failed to validate analysis",
        "details": e.errors(),
        "raw_output": result
        }
    except Exception:
        analysis = {
        "error": "Failed to parse model output",
        "raw_output": result
    }

    return context.model_copy(
        update={
            "analysis": analysis,
            "analysis_error": None,
            "raw_analysis_output": None,
        }
    )
