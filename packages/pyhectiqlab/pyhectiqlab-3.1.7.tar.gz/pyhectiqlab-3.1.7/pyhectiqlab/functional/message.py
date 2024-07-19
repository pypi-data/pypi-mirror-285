from .utils import expose_static_methods
from pyhectiqlab.message import Message

"""
Functional message API. To expose a function, use the `exposed_method` decorator in the singleton.
"""

locals().update(expose_static_methods(Message))
