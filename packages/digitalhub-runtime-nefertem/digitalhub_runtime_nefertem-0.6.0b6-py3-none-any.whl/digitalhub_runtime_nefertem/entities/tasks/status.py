from __future__ import annotations

from digitalhub_core.entities.tasks.status import TaskStatus


class TaskStatusInfer(TaskStatus):
    """
    Task Infer status.
    """


class TaskStatusProfile(TaskStatus):
    """
    Task Profile status.
    """


class TaskStatusValidate(TaskStatus):
    """
    Task Validate status.
    """


class TaskStatusMetric(TaskStatus):
    """
    Task Metric status.
    """
