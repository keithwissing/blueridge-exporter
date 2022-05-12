import functools
import os
import pickle
import string
from time import monotonic_ns
from typing import Any

def timed_memory_cache(_func=None, *, seconds: int = 7000, maxsize: int = 128, typed: bool = False) -> Any:
    """
    A function that creates a decorator with a time limited lru_cache
    """

    def decorator(fn: Any) -> Any:
        f = functools.lru_cache(maxsize=maxsize, typed=typed)(fn)
        f.delta = seconds * 10 ** 9
        f.expiration = monotonic_ns() + f.delta

        @functools.wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            if monotonic_ns() >= f.expiration:
                f.cache_clear()
                f.expiration = monotonic_ns() + f.delta
            return f(*args, **kwargs)

        wrapped.cache_info = f.cache_info
        wrapped.cache_clear = f.cache_clear

        return wrapped

    return decorator

def clean_filename(filename: str) -> str:
    whitelist = set(string.ascii_letters + string.digits + string.digits + '~!@#$%^&*()-_=+[{}];,.?')
    return ''.join(c for c in filename if c in whitelist)

def file_cache() -> Any:
    """
    A function that creates a decorator which will use "cachefile" for caching the results of the decorated function "fn".
    """

    def decorator(fn: Any) -> Any:  # define a decorator for a function "fn"
        @functools.wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:  # define a wrapper that will finally call "fn" with all arguments

            parts = [fn.__name__]
            # if args:
            #     parts.append('_'.join([str(x) for x in args]))
            # if kwargs:
            #     parts.append('_'.join([f'{str(k)}-{str(v)}' for k, v in kwargs.items()]))
            cachefile = clean_filename('_'.join(parts) + '.pickle')

            # if cache exists -> load it and return its content
            if os.path.exists(cachefile):
                with open(cachefile, 'rb') as cache_handle:
                    # print(f"using cached result from '{cachefile}'")
                    return pickle.load(cache_handle)

            # execute the function with all arguments passed
            res = fn(*args, **kwargs)

            # write to cache file
            with open(cachefile, 'wb') as cache_handle:
                # print(f"saving result to cache '{cachefile}'")
                pickle.dump(res, cache_handle)

            return res

        return wrapped

    return decorator  # return this "customized" decorator that uses "cachefile"
