import ast

from app.models.analysis_models import AnalysisIR
from app.models.static_analysis_models import StaticAnalysisReport


def analyze_generated_code(
    python_code: str,
    analysis: AnalysisIR,
) -> StaticAnalysisReport:
    """
    Deterministically analyze generated Python code.

    This performs structural validation only.
    No LLMs are used here.
    """

    tree = ast.parse(python_code)

    implemented_functions = set()
    implemented_classes = set()
    implemented_variables = set()

    # Walk the AST once
    for node in ast.walk(tree):

        # Collect functions
        if isinstance(node, ast.FunctionDef):
            if node.name != "__init__":
                implemented_functions.add(node.name)

        # Collect classes
        elif isinstance(node, ast.ClassDef):
            implemented_classes.add(node.name)

        # Collect assigned variables
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    implemented_variables.add(target.id)

    # -----------------------------
    # Compare against the IR
    # -----------------------------

    expected_functions = {
        function.name
        for function in analysis.functions
    }

    expected_variables = {
        variable.name
        for variable in analysis.variables
    }

    matched_functions = expected_functions & implemented_functions
    missing_functions = expected_functions - implemented_functions

    matched_variables = expected_variables & implemented_variables
    missing_variables = expected_variables - implemented_variables

    return StaticAnalysisReport(
        functions_total=len(expected_functions),
        functions_matched=len(matched_functions),
        missing_functions=sorted(missing_functions),
        implemented_functions=sorted(implemented_functions),
        variables_total=len(expected_variables),
        variables_matched=len(matched_variables),
        missing_variables=sorted(missing_variables),
        implemented_variables=sorted(implemented_variables),
        implemented_classes=sorted(implemented_classes),
    )
