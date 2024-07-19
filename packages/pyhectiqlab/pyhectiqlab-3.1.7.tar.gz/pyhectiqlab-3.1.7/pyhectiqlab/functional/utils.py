from typing import Any, Dict, Callable


def expose_static_methods(cls) -> Dict[str, Callable[..., Any]]:
    """Expose all static methods of a class to a module namespace."""
    namespace = {}
    for name, method in cls.__dict__.items():
        if method.__class__ != staticmethod:
            continue
        method = getattr(cls, name)
        if not hasattr(method, "exposed") or not method.exposed:
            continue
        namespace[method.alias or method.__name__] = method
    return namespace
