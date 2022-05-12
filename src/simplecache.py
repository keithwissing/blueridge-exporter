import functools
import os
import pickle
import string
from typing import Any

def clean_filename(filename: str) -> str:
    whitelist = set(string.ascii_letters + string.digits + string.digits + '~!@#$%^&*()-_=+[{}];,.?')
    return ''.join(c for c in filename if c in whitelist)

def file_cached() -> Any:
    """
    A function that creates a decorator which will use "cachefile" for caching the results of the decorated function "fn".
    """

    def decorator(fn: Any) -> Any:  # define a decorator for a function "fn"
        @functools.wraps(fn)
        def wrapped(*args: Any,
                    **kwargs: Any) -> Any:  # define a wrapper that will finally call "fn" with all arguments

            parts = [fn.__name__]
            # if args:
            #     parts.append('_'.join([str(x) for x in args]))
            # if kwargs:
            #     parts.append('_'.join([f'{str(k)}-{str(v)}' for k, v in kwargs.items()]))
            cachefile = clean_filename('_'.join(parts) + '.pickle')

            # if cache exists -> load it and return its content
            if os.path.exists(cachefile):
                with open(cachefile, 'rb') as cachehandle:
                    # print(f"using cached result from '{cachefile}'")
                    return pickle.load(cachehandle)

            # execute the function with all arguments passed
            res = fn(*args, **kwargs)

            # write to cache file
            with open(cachefile, 'wb') as cachehandle:
                # print(f"saving result to cache '{cachefile}'")
                pickle.dump(res, cachehandle)

            return res

        return wrapped

    return decorator  # return this "customized" decorator that uses "cachefile"
