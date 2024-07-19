"""Proxy functions for QuClo."""

from functools import wraps
import requests
from quclo.utils import QUCLO_API_URL
from quclo.models import Priority


def proxy(
    func=None,
    *,
    url: str = QUCLO_API_URL,
    api_key: str | None = None,
    priority: Priority | None = None,
):
    """Function and decorator to proxy requests globally or locally."""

    def set_proxy(name: str = "quclo_post"):
        if requests.post.__name__ == name:
            return requests.post
        else:
            original_post = requests.post
            requests.post = lambda *args, **kwargs: original_post(url, *args, **kwargs)
            requests.post.__name__ = name
            return original_post

    def decorator(inner_func):
        @wraps(inner_func)
        def wrapper(*args, **kwargs):
            original_post = set_proxy()
            try:
                return inner_func(*args, **kwargs)
            finally:
                requests.post = original_post

        return wrapper

    if func is None:
        set_proxy()
        return decorator
    elif callable(func):
        return decorator(func)
    else:
        raise ValueError("Invalid argument provided")
