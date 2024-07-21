from enum import Enum


class Direction(Enum):
    LONG = "long"
    SHORT = "short"


class ProfitPossibility(Enum):
    """Profit possibility for take profit, each possibility has its own fibonacci retracement number.

    The detail fibonacci number related in :mod:`tradex.constants.listting`"""

    LOW = "low"
    MARKET = "market"
    AGGRESSIVE = "aggressive"
