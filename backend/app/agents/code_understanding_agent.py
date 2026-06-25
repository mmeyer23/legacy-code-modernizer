import json
from app.services.llm_service import analyze_code


def build_analysis_prompt(fortran_code: str) -> str:
    return f"""
You are an expert software engineer specializing in legacy system modernization.

Analyze the following Fortran code and return ONLY valid JSON.

DO NOT include markdown, explanations, or text outside JSON.

Return exactly this structure:

{{
  "summary": "string",
  "inputs": ["string"],
  "outputs": ["string"],
  "variables": ["string"],
  "functions": ["string"],
  "data_flow": ["string"],
  "migration_challenges": ["string"]
}}

Rules:
- Be precise and concise
- Use bullet-like short strings in arrays
- If something is unknown, infer conservatively
- Ensure valid JSON only

Fortran Code:
----------------
{fortran_code}
----------------
"""


def analyze_fortran_code(fortran_code: str):
    prompt = build_analysis_prompt(fortran_code)
    result = analyze_code(prompt)

    try:
        return json.loads(result)
    except Exception:
        return {
            "error": "Failed to parse model output",
            "raw_output": result
        }