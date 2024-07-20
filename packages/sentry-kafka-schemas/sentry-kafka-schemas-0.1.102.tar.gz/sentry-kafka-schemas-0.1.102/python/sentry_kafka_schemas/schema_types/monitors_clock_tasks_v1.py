from typing import Required, Literal, Union, TypedDict


class MarkMissing(TypedDict, total=False):
    """
    mark_missing.

    Indicates a monitor ID that should be marked as missed.
    """

    type: Required[Literal['mark_missing']]
    """
    Discriminant marker identifying the task.

    Required property
    """

    ts: Required[Union[int, float]]
    """
    The timestamp the clock ticked at.

    Required property
    """

    monitor_environment_id: Required[Union[int, float]]
    """
    The monitor environment ID to generate a missed check-in for.

    Required property
    """



class MarkTimeout(TypedDict, total=False):
    """
    mark_timeout.

    Indicates a check-in should be marked as having timed out.
    """

    type: Required[Literal['mark_timeout']]
    """
    Discriminant marker identifying the task.

    Required property
    """

    ts: Required[Union[int, float]]
    """
    The timestamp the clock ticked at.

    Required property
    """

    monitor_environment_id: Required[Union[int, float]]
    """
    The monitor environment ID the check-in is part of.

    Required property
    """

    checkin_id: Required[Union[int, float]]
    """
    The check-in ID to mark as timed out.

    Required property
    """



MonitorsClockTasks = Union["MarkTimeout", "MarkMissing"]
"""
monitors_clock_tasks.

Aggregation type: oneOf
"""

