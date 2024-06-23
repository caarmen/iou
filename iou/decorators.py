import functools
import os


def ensure_envvar_set(envvar_name: str):
    """
    Only call the wrapped function if the given environment variable is defined.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if os.getenv(envvar_name):
                func(*args, **kwargs)

        return wrapper

    return decorator
