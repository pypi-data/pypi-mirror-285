from pyhectiqlab.block import Block
from .utils import expose_static_methods

locals().update(expose_static_methods(Block))
