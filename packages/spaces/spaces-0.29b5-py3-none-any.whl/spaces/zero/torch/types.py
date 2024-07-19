"""
"""
from __future__ import annotations

from typing import NamedTuple

import torch


class AliasId(NamedTuple):
    data_ptr: int
    size: int
    storage_offset: int
    shape: tuple[int, ...]
    stride: tuple[int, ...]

    @classmethod
    def from_tensor(cls, tensor: torch.Tensor):
        storage: torch.UntypedStorage = tensor.untyped_storage() # pyright: ignore [reportAssignmentType]
        return cls(
            storage.data_ptr(),
            storage.size(),
            tensor.storage_offset(),
            tensor.shape,
            tensor.stride(),
        )
