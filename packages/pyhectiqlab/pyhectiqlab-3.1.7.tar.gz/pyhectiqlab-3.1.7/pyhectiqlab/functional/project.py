from pyhectiqlab.project import Project
from .utils import expose_static_methods

locals().update(expose_static_methods(Project))
