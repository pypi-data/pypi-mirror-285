import pytest

from tradex.utils.fibonacci import fib_retrace, fib_retrace_default, fib_retrace_standalone


@pytest.mark.parametrize(
    ("start", "middle", "fib_val", "expected"),
    [
        (0, 1, 0.382, 0.382),
        (1, 0, 0.26, 0.74),
        (69862.4, 65078, 0.618, 66905.641),
        (38555, 52816.62, 0.382, 44002.939),
    ],
)
def test_fib_retrace_standalone(start, middle, fib_val, expected):
    val = fib_retrace_standalone(start=start, middle=middle, fib_val=fib_val)
    assert val == expected


@pytest.mark.parametrize(
    ("start", "middle", "fib_stand", "expected"),
    [
        (0, 1, [0.26, 0.382, 0.618], [0.26, 0.382, 0.618]),
        (1, 0, [0.26, 0.382, 0.618], [0.74, 0.618, 0.382]),
        (69862.4, 65078, [0.26, 0.382, 0.618], [68618.456, 68034.759, 66905.641]),
        (38555, 52816.62, [0.26, 0.382, 0.618], [42263.021, 44002.939, 47368.681]),
    ],
)
def test_fib_retrace(start, middle, fib_stand, expected):
    fib_retrace_output = fib_retrace(start=start, middle=middle, fib_stand=fib_stand)
    assert fib_retrace_output == expected


@pytest.mark.parametrize(
    ("start", "middle", "expected"),
    [
        (0, 1, [0, 0.382, 0.5, 0.618, 0.786, 1, 1.272, 1.382, 1.5, 1.618, 2, 2.618, 3]),
        (1, 0, [1, 0.618, 0.5, 0.382, 0.214, 0, -0.272, -0.382, -0.5, -0.618, -1, -1.618, -2]),
        (
            69862.4,
            65078,
            [
                69862.4,
                68034.759,
                67470.2,
                66905.641,
                66101.862,
                65078,
                63776.643,
                63250.359,
                62685.8,
                62121.241,
                60293.6,
                57336.841,
                55509.2,
            ],
        ),
        (
            38555,
            52816.62,
            [
                38555.0,
                44002.939,
                45685.81,
                47368.681,
                49764.633,
                52816.62,
                56695.781,
                58264.559,
                59947.43,
                61630.301,
                67078.24,
                75891.921,
                81339.86,
            ],
        ),
    ],
)
def test_fib_retrace_default(start, middle, expected):
    fib_retrace_output = fib_retrace_default(start=start, middle=middle)
    assert fib_retrace_output == expected
