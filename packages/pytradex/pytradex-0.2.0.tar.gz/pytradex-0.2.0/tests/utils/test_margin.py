import pytest

from tradex.utils.margin import Margin


@pytest.mark.parametrize(
    ("size", "leverage", "margin"),
    [
        (10000, 10, 1000),
        (10000, 1, 10000),
        (3357.4, 125, 26.8592),
    ],
)
def test_margin(size, leverage, margin):
    m = Margin(size=size, leverage=leverage)
    assert margin == m.margin, f"Expected margin is {margin} but got {m.margin}"


@pytest.mark.parametrize(
    ("size", "leverage"),
    [
        (10000, -10),
        (-10000, 10),
    ],
)
def test_margin_invalid(size, leverage):
    with pytest.raises(ValueError, match="must be positive"):
        Margin(size=size, leverage=leverage)
