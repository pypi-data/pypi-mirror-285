"""Integration module."""

def sum_function(float_unary_operator, start: float, end: float, parts: int):
    """Computes the integration of the given function between to values, splitting the interval in a given number of
    parts."""
    width: float = (end - start) / parts

    s = 0.
    for i in range(parts):
        x0: float = start + i * width + width / 2.0
        s += float_unary_operator(x0) * width
    return s
