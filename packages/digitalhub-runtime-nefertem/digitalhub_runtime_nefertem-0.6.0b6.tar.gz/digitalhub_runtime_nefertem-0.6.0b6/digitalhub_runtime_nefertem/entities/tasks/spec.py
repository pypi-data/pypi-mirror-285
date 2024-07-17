from __future__ import annotations

from digitalhub_core.entities.tasks.spec import TaskParamsK8s, TaskSpecK8s


class TaskSpecNefertem(TaskSpecK8s):
    """Task Nefertem specification."""

    def __init__(
        self,
        function: str,
        framework: str,
        exec_args: dict | None = None,
        parallel: bool = False,
        num_worker: int | None = 1,
        **kwargs,
    ) -> None:
        super().__init__(function, **kwargs)

        self.framework = framework
        self.exec_args = exec_args
        self.parallel = parallel
        self.num_worker = num_worker


class TaskParamsNefertem(TaskParamsK8s):
    """
    TaskParamsNefertem model.
    """

    framework: str
    """Nefertem framework."""

    exec_args: dict = {}
    """Nefertem execution arguments."""

    parallel: bool = False
    """Nefertem parallel execution."""

    num_worker: int = 1
    """Nefertem number of workers."""


###########################
# Inference
###########################


class TaskSpecInfer(TaskSpecNefertem):
    """Task Infer specification."""


class TaskParamsInfer(TaskParamsNefertem):
    """
    TaskParamsInfer model.
    """


###########################
# Profiling
###########################


class TaskSpecProfile(TaskSpecNefertem):
    """Task Profile specification."""


class TaskParamsProfile(TaskParamsNefertem):
    """
    TaskParamsProfile model.
    """


###########################
# Validation
###########################


class TaskSpecValidate(TaskSpecNefertem):
    """Task Validate specification."""


class TaskParamsValidate(TaskParamsNefertem):
    """
    TaskParamsValidate model.
    """


###########################
# Metric
###########################


class TaskSpecMetric(TaskSpecNefertem):
    """Task Metric specification."""


class TaskParamsMetric(TaskParamsNefertem):
    """
    TaskParamsMetric model.
    """
