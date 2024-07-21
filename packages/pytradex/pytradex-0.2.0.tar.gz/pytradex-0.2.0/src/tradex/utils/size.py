from dataclasses import dataclass

from tradex.constants.enuming import Direction


@dataclass
class Size:
    """Size of a trade, using the buy, defend and profit values

    :param buy: price at which the asset was bought
    :param defend: price at which the asset was defended, when price at the defend we should sell it
    :param loss: max loss for the trade
    """

    buy: float
    defend: float
    loss: float

    def __post_init__(self):
        if self.buy < 0 or self.defend < 0 or self.loss < 0:
            raise ValueError("Size arguments cannot be negative, check your profit settings")
        self.diff = self.buy - self.defend if self._is_long else self.defend - self.buy
        if self.diff == 0:
            raise ValueError("Price difference cannot be zero, check your buy and defend prices")

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(buy={self.buy!r}, defend={self.defend!r}, loss={self.loss!r}, "
            f"direction={self.direction.value}, size={self.size!r})"
        )

    @property
    def _is_long(self) -> bool:
        return self.buy > self.defend

    @property
    def direction(self) -> Direction:
        return Direction.LONG if self._is_long else Direction.SHORT

    @property
    def size(self) -> float:
        return round(self.loss * (self.buy / self.diff), 2)
