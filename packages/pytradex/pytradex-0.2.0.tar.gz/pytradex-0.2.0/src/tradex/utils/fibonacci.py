from tradex.constants.listting import FIB


def fib_retrace_standalone(*, start: float, middle: float, fib_val: float) -> float:
    return round(start + (middle - start) * fib_val, 3)


def fib_retrace(*, start: float, middle: float, fib_stand: list[float]) -> list[float]:
    """Fibonacci retracement levels for a given range."""
    return [fib_retrace_standalone(start=start, middle=middle, fib_val=level) for level in fib_stand]


def fib_retrace_default(*, start: float, middle: float) -> list[float]:
    """Fibonacci retracement levels for default range."""
    return fib_retrace(start=start, middle=middle, fib_stand=FIB)
