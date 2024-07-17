"""
"""

from ...config import Config


try:

    import torch

except ImportError:

    _patch = lambda *args, **kwargs: None
    _unpatch = lambda *args, **kwargs: None
    _pack = lambda *args, **kwargs: None
    _move = lambda *args, **kwargs: None
    _is_in_bad_fork = lambda *args, **kwargs: False

else:

    if Config.zero_gpu_v2:
        from . import patching as _patching
    else: # pragma: no cover
        from . import patching_legacy as _patching

    _patch = _patching.patch
    _unpatch = _patching.unpatch
    _pack = _patching.pack
    _move = _patching.move
    _is_in_bad_fork = _patching.is_in_bad_fork

patch = _patch
unpatch = _unpatch
pack = _pack
move = _move
is_in_bad_fork = _is_in_bad_fork
