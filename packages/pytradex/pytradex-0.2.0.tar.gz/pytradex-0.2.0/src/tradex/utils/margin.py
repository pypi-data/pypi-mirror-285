from dataclasses import dataclass


@dataclass
class Margin:
    """Margin of a future trade, using the size and leverage values

    :param size: total size of amount to be traded, will be the :class:`Position.position` value after we
        order the trade
    :param leverage: leverage of the trade
    """

    size: float
    leverage: int

    @property
    def margin(self) -> float:
        return self.size / self.leverage

    def __post_init__(self):
        if self.size < 0:
            raise ValueError("Size must be positive")
        if self.leverage < 0:
            raise ValueError("Leverage must be positive")

    def __repr__(self):
        return f"{self.__class__.__name__}(size={self.size!r}, leverage={self.leverage!r}, margin={self.margin!r})"
