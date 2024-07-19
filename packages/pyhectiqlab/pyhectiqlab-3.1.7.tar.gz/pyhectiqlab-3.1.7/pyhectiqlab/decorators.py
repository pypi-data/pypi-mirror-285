from functools import wraps
from typing import Optional, Union

from pyhectiqlab.settings import getenv
from pyhectiqlab.logging import hectiqlab_logger


class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


def execute_online_only(f):
    """Decorator to execute a function only if the client is online.
    If the client is offline, the function is not executed and a log message is displayed.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        from pyhectiqlab.client import Client

        if not Client.online():
            if not hasattr(f, "_show_online_only_error"):
                if getenv("HECTIQLAB_LOG_LEVEL", "warning").lower() == "debug":
                    msg = f"`{f.__name__}` with args {list(args)} and kwargs {kwargs} not executed. Offline mode."
                else:
                    msg = f"`{f.__name__}` not executed. Offline mode."
                hectiqlab_logger.error(msg)
                f._show_online_only_error = False
            return
        return f(*args, **kwargs)

    return wrapper


def no_git_diff(force: bool = False):

    def _wrapper(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            from pyhectiqlab.project import Project
            from pyhectiqlab.client import Client
            from pyhectiqlab.versions import PackageVersion

            if force:
                return f(*args, **kwargs)
            if not Project.allow_dirty() and PackageVersion.is_dirty():
                hectiqlab_logger.error(f"`{f.__name__}` not executed. There are uncommited changes in the repository.")
                Client.online(False)
            return f(*args, **kwargs)

        return wrapper

    return _wrapper


def beta(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        hectiqlab_logger.error("This method is still in development and can be unstable.")
        return f(self, *args, **kwargs)

    return wrapper


def will_be_depreciated(suggested_method):
    def _method(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            hectiqlab_logger.error(
                f"The method `{f.__name__}` will be removed in a future release. Use `{suggested_method}` instead."
            )
            return f(self, *args, **kwargs)

        return wrapper

    return _method


def functional_alias(alias: Optional[str] = None):
    def _exposed_method(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        wrapper.exposed = True
        wrapper.alias = alias or f.__name__
        return wrapper

    return _exposed_method


def request_handle(f: callable):
    """Use this over httpx.request to handle the response and the errors.
    Instead of returning the response, return the response.json() if the status code is 200.
    If the status code is not 200, log the error and return None.
    """

    def wrapper(*args, **kwargs) -> Union[dict, bytes, None]:
        response = f(*args, **kwargs)
        if response.status_code != 200:
            hectiqlab_logger.error(f"Request failed with status code {response.status_code}: {response.content}")
            return None
        try:
            return response.json()
        except:
            return response.content

    return wrapper
