from typing import Optional, Callable, Union
from deprecated.sphinx import versionadded
import multiprocessing as mp

try:
    import numba
except ImportError as _:
    numba = None

def integrate_segment(func: Callable, start: float, end: float, dx: float, n: int) -> float:
    total_area = func(start) + func(end)
    sum_odd = 0.0
    sum_even = 0.0

    for i in range(1, n):
        x = start + i * dx
        f_x = func(x)
        if i % 2 == 0:
            sum_even += f_x
        else:
            sum_odd += f_x

    total_area += 4 * sum_odd + 2 * sum_even
    total_area *= dx / 3
    return total_area

def integrate(func: Callable, start: Optional[int | float] = 0, end: Optional[int | float] = 1, dx: Optional[int | float] = None) -> float:
    if dx is None:
        dx = 1e-6  # Default small step size

    n = int((end - start) / dx)
    if n % 2 == 1:  # Ensure n is even
        n += 1

    dx = (end - start) / n
    num_processes = mp.cpu_count()
    segment_size = (end - start) / num_processes
    segment_n = n // num_processes

    with mp.Pool(processes=num_processes) as pool:
        results = [
            pool.apply_async(integrate_segment, (func, start + i * segment_size, start + (i + 1) * segment_size, dx, segment_n))
            for i in range(num_processes)
        ]
        segment_areas = [result.get() for result in results]

    total_area = sum(segment_areas)
    return total_area