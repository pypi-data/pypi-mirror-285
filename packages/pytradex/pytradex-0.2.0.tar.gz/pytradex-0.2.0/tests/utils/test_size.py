import pytest

from tradex.constants.enuming import Direction
from tradex.utils.size import Size


@pytest.mark.parametrize(
    ("buy", "defend", "loss", "size", "direction"),
    [
        # long order
        (10000, 9500, 1000, 20000, Direction.LONG),
        (3350, 3122, 1000, 14692.98, Direction.LONG),
        (3350, 10, 1000, 1002.99, Direction.LONG),
        # short order
        (10000, 10500, 1000, 20000, Direction.SHORT),
        (3350, 3500, 1000, 22333.33, Direction.SHORT),
        (10, 3350, 1000, 2.99, Direction.SHORT),
    ],
)
def test_size_prop(buy, defend, loss, size, direction):
    s = Size(buy=buy, defend=defend, loss=loss)
    assert size == s.size, f"Expected size is {size} but got {s.size}"
    assert direction == s.direction, f"Expected direction is {direction} but got {s.direction}"


@pytest.mark.parametrize(
    ("buy", "defend", "loss"),
    [
        (10000, 9500, -1000),
        (10000, -9500, 1000),
        (-10000, 9500, 1000),
    ],
)
def test_size_invalid(buy, defend, loss):
    with pytest.raises(ValueError, match="Size arguments cannot be negative"):
        Size(buy=buy, defend=defend, loss=loss)
