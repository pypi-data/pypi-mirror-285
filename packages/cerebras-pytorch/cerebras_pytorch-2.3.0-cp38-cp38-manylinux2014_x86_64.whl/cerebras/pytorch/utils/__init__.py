# Copyright 2016-2023 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

"""Emulates torch.utils."""
from cerebras.appliance.CSConfig import CSConfig

from . import benchmark
from .constant import make_constant
from .data import (
    DataExecutor,
    DataLoader,
    RestartableDataLoader,
    SyntheticDataset,
)

__all__ = ["DataLoader", "SyntheticDataset", "CSConfig"]
