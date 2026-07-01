from pydantic import BaseModel


class StaticAnalysisReport(BaseModel):
    functions_total: int
    functions_matched: int
    missing_functions: list[str]
    implemented_functions: list[str]

    variables_total: int
    variables_matched: int
    missing_variables: list[str]
    implemented_variables: list[str]

    implemented_classes: list[str]