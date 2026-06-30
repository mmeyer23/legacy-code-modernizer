from pydantic import BaseModel


class FunctionIR(BaseModel):
    name: str
    purpose: str
    parameters: list[str]
    returns: str
    calls: list[str]


class VariableIR(BaseModel):
    name: str
    type: str
    purpose: str


class AnalysisIR(BaseModel):
    summary: str

    inputs: list[str]

    outputs: list[str]

    variables: list[VariableIR]

    functions: list[FunctionIR]

    data_flow: list[str]

    migration_challenges: list[str]