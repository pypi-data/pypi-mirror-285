from typing import Required, Union, Dict, TypedDict


class MetricsSummary(TypedDict, total=False):
    """
    metrics_summary.

    anyOf:
      - required:
        - max
      - required:
        - min
      - required:
        - sum
    """

    duration_ms: Required["_Uint32"]
    """
    minimum: 0
    maximum: 4294967295

    Required property
    """

    end_timestamp: Required["_PositiveFloat"]
    """
    minimum: 0

    Required property
    """

    group: Required[str]
    """ Required property """

    is_segment: Required[bool]
    """ Required property """

    mri: Required[str]
    """ Required property """

    project_id: Required["_Uint64"]
    """
    minimum: 0

    Required property
    """

    received: Required["_PositiveFloat"]
    """
    minimum: 0

    Required property
    """

    retention_days: Required["_Uint16"]
    """
    minimum: 0
    maximum: 65535

    Required property
    """

    segment_id: Required[str]
    """ Required property """

    span_id: Required[str]
    """ Required property """

    trace_id: Required["_Uuid"]
    """
    minLength: 32
    maxLength: 36

    Required property
    """

    count: int
    """ minimum: 1 """

    max: Union[int, float]
    min: Union[int, float]
    sum: Union[int, float]
    tags: Dict[str, str]


_PositiveFloat = Union[int, float]
""" minimum: 0 """



_Uint16 = int
"""
minimum: 0
maximum: 65535
"""



_Uint32 = int
"""
minimum: 0
maximum: 4294967295
"""



_Uint64 = int
""" minimum: 0 """



_Uuid = str
"""
minLength: 32
maxLength: 36
"""

