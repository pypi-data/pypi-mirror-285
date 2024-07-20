# Copyright 2016-2023 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

""" Contains the CPU backend subclass """
from warnings import warn

from cerebras.appliance.log import ClassLogger, named_class_logger
from cerebras.pytorch.backend.base_backend import BaseBackend
from cerebras.pytorch.core.device import CPUDevice
from cerebras.pytorch.saver.pt_h5_saver import PyTorchH5Saver

UNSPECIFIED = object


@named_class_logger("CpuBackend")
class CpuBackendImpl(BaseBackend, ClassLogger):
    """The CPU backend subclass"""

    def __init__(
        self,
        backend_type,
        artifact_dir: str = None,
        mixed_precision: bool = UNSPECIFIED,
    ):
        super().__init__(backend_type, CPUDevice(), artifact_dir)

        if mixed_precision is not UNSPECIFIED:
            warn(
                f"Passing mixed_precision to the CPU backend is deprecated. "
                f"Please use the cstorch.amp.autocast() context manager instead."
            )

    def on_run_start(self):
        """Runs once at the beginning of the run

        Used by cstorch.utils.data.DataLoader
        """
        super().on_run_start()
        self.run_step_closures()

    def save(self, state_dict, checkpoint_file):  # pylint: disable=no-self-use
        """
        Save the provided state dict to a checkpoint at the provided filepath
        """
        saver = PyTorchH5Saver()
        saver.save(checkpoint_file, state_dict)
