from typing import Required, Union, Literal, TypedDict


class CheckConfig(TypedDict, total=False):
    """
    check_config.

    A message containing the configuration for a check to scheduled and executed by the uptime-checker.
    """

    subscription_id: Required[str]
    """
    UUID of the subscription that this check config represents.

    Required property
    """

    interval_seconds: Required["CheckInterval"]
    """
    check_interval.

    The interval between each check run in seconds.

    Required property
    """

    timeout_ms: Required[Union[int, float]]
    """
    The total time we will allow to make the request in milliseconds.

    Required property
    """

    url: Required[str]
    """
    The actual HTTP URL to check.

    Required property
    """



CheckInterval = Union[Literal[60], Literal[300], Literal[600], Literal[1200], Literal[1800], Literal[3600]]
"""
check_interval.

The interval between each check run in seconds.
"""
CHECKINTERVAL_60: Literal[60] = 60
"""The values for the 'check_interval' enum"""
CHECKINTERVAL_300: Literal[300] = 300
"""The values for the 'check_interval' enum"""
CHECKINTERVAL_600: Literal[600] = 600
"""The values for the 'check_interval' enum"""
CHECKINTERVAL_1200: Literal[1200] = 1200
"""The values for the 'check_interval' enum"""
CHECKINTERVAL_1800: Literal[1800] = 1800
"""The values for the 'check_interval' enum"""
CHECKINTERVAL_3600: Literal[3600] = 3600
"""The values for the 'check_interval' enum"""

