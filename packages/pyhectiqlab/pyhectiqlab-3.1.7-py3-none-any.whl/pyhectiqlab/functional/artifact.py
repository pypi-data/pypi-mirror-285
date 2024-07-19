from pyhectiqlab.artifact import Artifact
from .utils import expose_static_methods

"""
Functional run API. To expose a function, use the `exposed_method` decorator in the `Run` singleton.
"""

locals().update(expose_static_methods(Artifact))
