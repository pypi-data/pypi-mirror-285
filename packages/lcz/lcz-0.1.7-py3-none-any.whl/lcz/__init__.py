"""
### Lcz
> Python bindings for Leela Chess Zero, simplified
"""
from .main import eval, Uci, Prob
from .backends import available_backends, cached_backend
from .weights import MAIA_PATH