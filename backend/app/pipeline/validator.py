import json

from app.models.migration_models import MigrationContext
from app.models.validation_models import ValidationReport
from app.services.llm_service import analyze_code


def build_validation_prompt(context: MigrationContext, generated_code: str) -> str:
    return f"""
You are a strict static analysis and code validation engine.

You evaluate correctness of generated code against an Intermediate Representation (IR) line-by-line.

You are NOT a reviewer.  You are a compiler-style validator.

## IR (ground truth specification)
{context.analysis.model_dump_json(indent=2) if context.analysis else "{}"}

## Generated Python code
{generated_code}

---

# TASKS (MUST FOLLOW EXACTLY)

## 1. FUNCTION COVERAGE CHECK
Compare IR functions vs Python functions.

Compute:
- functions_total = number of functions in IR
- functions_matched = number of IR functions implemented in Python

A function is ONLY matched if it is:
- explicitly implemented
- not a placeholder (no "pass", no "return 'Unknown'")

---

## 2. VARIABLE COVERAGE CHECK
Compare IR variables vs Python variables.

Compute:
- variables_total
- variables_matched

A variable is matched if:
- it is explicitly represented in Python code
- not replaced with dummy placeholders unless justified by IR

---

## 3. PLACEHOLDER DETECTION (CRITICAL)
Identify any placeholder or non-implemented logic.

Examples:
- pass
- return "Unknown"
- return None (when logic expected)
- dummy arrays like [0] * n
- empty function bodies

Each placeholder must be penalized.

---

## 4. HALLUCINATION DETECTION
Flag any:
- functions not in IR
- logic not supported by IR
- extra behavior introduced by model

---

# SCORING RULES (HARD ENFORCED)

Start with:

100 points

Apply penalties:

- placeholder_logic (function) → -20 each
- placeholder_logic (variable misuse) → -10 each
- missing_function → -25 each
- mapping_error → -10 each
- hallucination → -30 each

Final score MUST reflect ALL penalties.

Clamp score between 0 and 100.

---

# CATEGORY RULES (STRICT ENUM ONLY)

All issue categories MUST be EXACTLY one of:

- missing_function
- mapping_error
- placeholder_logic
- hallucination

Category usage rules:

- Use "missing_function" ONLY when an IR function does not exist anywhere in the generated code.

- If a function exists but contains only placeholder logic (such as "pass", "return Unknown", "return None", or an empty body), classify it as "placeholder_logic".

Do not classify placeholder implementations as missing functions.

---

## OUTPUT FORMAT (STRICT JSON)

{{
  "passed": true/false,

  "confidence_score": 0-100,

  "coverage": {{
    "functions_total": int,
    "functions_matched": int,
    "variables_total": int,
    "variables_matched": int
  }},

  "strengths": [],
  "issues": [
    {{
      "severity": "low|medium|high|critical",
      "category": "missing_function | mapping_error | placeholder_logic | hallucination",
      "message": "..."
    }}
  ],

  "recommendations": []
}}

---

# PASS/FAIL RULE

A result is ONLY "passed": true if:
- confidence_score >= 80
- AND no high or critical severity issues exist

Otherwise, passed MUST be false.

---

Return ONLY JSON. No explanation. No markdown.
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