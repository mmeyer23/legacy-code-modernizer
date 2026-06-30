from app.models.migration_models import MigrationContext
from app.services.llm_service import analyze_code


def build_migration_prompt(context: MigrationContext) -> str:
    return f"""
You are a deterministic code translation engine.

You are NOT allowed to invent new logic.

You must ONLY translate what is explicitly present in the structured analysis.

RULES:
- Do NOT guess or infer missing logic
- Do NOT create new weather codes or mappings
- Do NOT add features not described in inputs/outputs/functions
- Preserve behavior as closely as possible
- If logic is missing, implement a placeholder function with a comment

STRUCTURED ANALYSIS:
{context.analysis}

OUTPUT REQUIREMENTS:
- Output ONLY Python code
- No explanations
- No markdown
- Must be runnable Python
"""


def generate_python_code(context: MigrationContext) -> str:
    prompt = build_migration_prompt(context)
    return analyze_code(prompt)
