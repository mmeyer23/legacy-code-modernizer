from app.services.llm_service import analyze_code


def build_analysis_prompt(fortran_code: str) -> str:
    return f"""
Analyze the following Fortran code for migration to Python.

Return structured output with:

1. Summary of what the program does
2. Inputs
3. Outputs
4. Key variables
5. Key functions/subroutines
6. Data flow
7. Potential migration challenges

Fortran Code:
----------------
{fortran_code}
----------------
"""


def analyze_fortran_code(fortran_code: str) -> str:
    prompt = build_analysis_prompt(fortran_code)
    return analyze_code(prompt)