from __future__ import annotations

from digitalhub_core.entities.functions.spec import FunctionParams, FunctionSpec


class FunctionSpecNefertem(FunctionSpec):
    """
    Specification for a Function Nefertem.
    """

    def __init__(
        self,
        constraints: list[dict] | None = None,
        error_report: str | None = None,
        metrics: list[dict] | None = None,
    ):
        super().__init__()
        self.constraints = constraints
        self.error_report = error_report
        self.metrics = metrics


class FunctionParamsNefertem(FunctionParams):
    """
    Function Nefertem parameters model.
    """

    constraints: list[dict] = None
    """List of constraints for the function."""

    error_report: str = None
    """Error report kind for the function."""

    metrics: list[dict] = None
    """List of metrics for the function."""
