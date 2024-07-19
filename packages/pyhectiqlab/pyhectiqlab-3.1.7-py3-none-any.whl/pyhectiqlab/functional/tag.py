from .utils import expose_static_methods
from pyhectiqlab.tag import Tag

locals().update(expose_static_methods(Tag))
