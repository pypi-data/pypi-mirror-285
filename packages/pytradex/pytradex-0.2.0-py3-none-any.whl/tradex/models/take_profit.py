from dataclasses import dataclass


@dataclass
class TPSL:
    volume: float
    price: float


@dataclass
class TakeProfit(TPSL):
    pass


@dataclass
class StopLoss(TPSL):
    pass
