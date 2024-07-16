try:
    import numpy as np
except ImportError as _:
    np = None

import math

def factorial(n: int) -> int:
    """
    Calculate the factorial of a number
    :param n: int
    :returns: int
        """
    if np:
        n = np.abs(n)

        return np.prod(np.arange(1, n + 1, dtype=int))
    else:
        n = abs(n)
        return math.prod(range(1, n + 1))

def fib(n: int) -> int:
    """
    Calculate the fibonacci sequence for a number recursively
    :param n: int
    :returns: int
    """
    if np:
        n = np.abs(n)
    else:
        n = abs(n)
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
