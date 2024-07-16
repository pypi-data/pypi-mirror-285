# eouTools
## Requirements
- python >= 3.10 (Required)
- python >= 3.12 (Suggested)
- numpy (Suggested)
- Deprecated (Required)
## eouTools.numbers
### isPositive
Syntax: isPositive(n: int | float) -> bool<br>
Alternative: `not isNegative(n)`<br>
Documentation: "Returns whether `n` is positive or not"

### isNegative
Syntax: `isNegative(n: int | float) -> bool`<br>
Alternative: `not isPositive(n)`<br>
Documentation: "Returns whether `n` is negative or not"

### isZero
Syntax: `isZero(n: int | float) -> bool`<br>
Alternative: `n == 0`<br>
Documentation: "Returns whether `n` is zero or not"

## eouTools.decorators
### rename_on_init
Syntax: `@rename_on_init(name: str)`<br>
Documentation: "Rename a function when it is initialized. This may raise unexpected behavior, however"

### retry
Syntax: `@retry(amount: Optional[int], stop_at: Optional[Tuple[Exception]])`<br>
Documentation: "Try calling the functon `amount` amount of times, but stop if the exception raised is in `stop_at` or if the function did not raise an error"

### cache
Syntax: `@cache`<br>
Documentation: "Create a cache of all results given by a function. run the `.clear_cache()` function to delete the cache. Can be used to speed up certain algorithms such as recursive Fibonacci sequence"

## eouTools.benchmarking.decorators
### time_func
Syntax: `@time_func`<br>
Documentation: "Time a function. Parse in the keyworded argument `_no_time = True` to get the return instead of the time it took to execute"

## eouTools.arithmetic_equations.integers
### factorial
Syntax: `factorial(n: int) -> int`<br>
Documentation: "Calculate the factorial of a number"<br>
Requirements: `numpy`

## eouTools.arithmetic_equations.integrals
### integrate
Syntax: `integrate(func: Callable, start: Optional[int | float], end: Optional[int | float], dx: Optional[int | float]) -> float`<br>
Documentation: [Self-Explanatory]<br>
Used Builtins: `multiprocessing`

### fib
Syntax: `fib(n: int) -> int`<br>
Documentation: `Calculate the fibonacci sequence for a number recursively`<br>
Requirements:
- numpy (suggested)