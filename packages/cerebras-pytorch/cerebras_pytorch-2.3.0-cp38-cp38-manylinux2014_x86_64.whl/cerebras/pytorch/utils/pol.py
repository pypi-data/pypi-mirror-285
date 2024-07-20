# Copyright 2016-2023 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from cerebras.appliance.utils.descriptor import Descriptor
from cerebras.pytorch.core.annotation import AnnotationMode, annotate


class PolAnnotationMode(AnnotationMode):
    @dataclass
    class PolConfig(AnnotationMode.Config):
        """Represents POL config"""

        level: Optional[int]
        bwd_level: Optional[int]

        def __post_init__(self):
            for name in ["level", "bwd_level"]:
                val = getattr(self, name)
                if val is not None and val not in range(0, 3):
                    raise ValueError(
                        f"POL must be None or an integer in range [0, 3) but got "
                        f"{'forward' if name == 'level' else 'backward'} level {val}."
                    )

    # Global POL config instance helps to handle nested annotation modes.
    _pol_config: Optional[PolConfig] = None

    @property
    def config(self):
        """POL global config getter"""
        return PolAnnotationMode._pol_config

    @config.setter
    def config(self, config: PolAnnotationMode.PolConfig):
        """POL global config setter"""
        PolAnnotationMode._pol_config = config

    def get_attribute(
        self, config: PolAnnotationMode.PolConfig, is_backward: bool
    ):
        """Returns POL attribute"""
        level = config.level
        if is_backward and config.bwd_level is not None:
            level = config.bwd_level
        return AnnotationMode.Attribute('pol', level)


def pol(
    level: Optional[int] = None,
    bwd_level: Optional[int] = None,
    enable_fwd: bool = True,
    enable_bwd: bool = True,
):
    """Enables POL annotation for the wrapped function."""
    return annotate(
        annotation_mode=PolAnnotationMode(
            config=PolAnnotationMode.PolConfig(
                level=level,
                bwd_level=bwd_level,
                enable_fwd=enable_fwd,
                enable_bwd=enable_bwd,
            ),
        ),
    )


class POL(Descriptor):
    def sanitize(self, value: int) -> int:
        if value not in range(0, 3):
            raise ValueError(
                f"{self.name} must be an integer in range [0, 3). Got {value}"
            )

        from cerebras.pytorch.lib import cerebras_pytorch_lib

        cerebras_pytorch_lib.set_pol(value)
        return value
