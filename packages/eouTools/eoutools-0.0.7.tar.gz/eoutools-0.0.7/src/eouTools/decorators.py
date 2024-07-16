from typing import Callable, Any, Dict, Optional, Tuple
from functools import wraps
from deprecated.sphinx import deprecated
from deprecated.sphinx import versionadded

class MemoizedFunction:
    def __init__(self, func: Callable):
        self.func = func
        self.cache: Dict[str, Any] = {}

    def delete_cache(self) -> None:
        self.cache = {}

    def __call__(self, *args, **kwargs) -> Any:
        key = str(args) + str(kwargs)
        if key not in self.cache:
            self.cache[key] = self.func(*args, **kwargs)
        return self.cache[key]

    def __getattr__(self, name: str) -> Any:
        return getattr(self.func, name)

@deprecated(version='0.0.6', reason="Unnecessary usage of a class. Replaced with an easier-to-remember alternative")
def memoize(func: Callable) -> MemoizedFunction:
    """Create a cache of all results given by a function. run the `.delete_cache()` function to delete the cache. Can be used to speed up certain algorithms such as recursive Fibonacci sequence"""
    memoized_function = MemoizedFunction(func)
    return memoized_function

@versionadded(reason="Better Alternative for @memoize", version = '0.0.6')
def cache(func: Callable) -> Callable:
    """Create a cache of all results given by a function. run the `.clear_cache()` function to delete the cache. Can be used to speed up certain algorithms such as recursive Fibonacci sequence"""
    _cache = {}
    def delete_cache() -> None:
        nonlocal _cache
        _cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        key = str(args) + str(kwargs)
        if not _cache.get(key, None):
            _cache[key] = func(*args, **kwargs)

        return _cache[key]
    setattr(wrapper, 'delete_cache', delete_cache)
    setattr(wrapper, 'clear_cache', delete_cache)

    return wrapper


def rename_on_init(name: str) -> Callable:
    """
    Rename a function when it is initialized. This may raise unexpected behavior, however
    :param name: str
    :returns: Callable
    """
    def decorator(func: Callable) -> Callable:
        func.__name__ = name

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return func(*args, **kwargs)

        return wrapper

    return decorator

@versionadded(version='0.0.6')
def retry(amount: Optional[int] = 3, stop_at: Optional[Tuple[Exception]] = None) -> Callable:
    """Try calling the functon `amount` amount of times, but stop if the exception raised is in `stop_at` or if the function did not raise an error"""
    if stop_at is None:
        stop_at = ()
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for _ in range(amount):
                try:
                    return func(*args, **kwargs)
                except BaseException as e:
                    if e in stop_at:
                        raise e
                    else:
                        pass
        return wrapper
    return decorator