from app.services.llm_service import analyze_code


def build_migration_prompt(analysis: dict) -> str:
    return f"""
You are a senior software engineer specializing in legacy system modernization.

You are given a structured analysis of a Fortran program.

Your job is to generate equivalent Python code that preserves behavior.

Rules:
- Output ONLY Python code
- No explanations
- No markdown
- Use clean, readable Python
- Prefer functions and classes where appropriate
- Preserve logic exactly
- Use comments to explain mappings from Fortran where helpful

Structured Analysis:
--------------------
{analysis}
--------------------

Return the full Python implementation.
"""


def generate_python_code(analysis: dict) -> str:
    prompt = build_migration_prompt(analysis)
    return analyze_code(prompt)