"""
### Lines Dataset
> Dead simple standard for storing/loading datasets as lines of text. Supports zstd compression.
"""
import lazy_loader as lazy
__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)