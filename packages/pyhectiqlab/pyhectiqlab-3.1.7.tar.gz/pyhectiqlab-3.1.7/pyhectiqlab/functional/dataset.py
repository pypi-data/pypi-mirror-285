from .utils import expose_static_methods
from pyhectiqlab.dataset import Dataset

"""
Functional dataset API. To expose a function, use the `exposed_method` decorator in the `Run` singleton.
"""

locals().update(expose_static_methods(Dataset))
