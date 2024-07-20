# Copyright 2016-2024 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause
""" Backends configuration flags. """

from dataclasses import dataclass
from typing import List, Literal, Optional, Union

import cerebras.appliance
from cerebras.appliance.cluster.config import FABRIC_TYPE_CS2, FABRIC_TYPE_CS3
from cerebras.appliance.utils.debug_args import DebugArgs, DebugArgsDescriptor
from cerebras.appliance.utils.descriptor import Descriptor
from cerebras.pytorch.core.compile import RetraceEveryIteration
from cerebras.pytorch.core.device import Config as DeviceConfig
from cerebras.pytorch.utils._flags import DEFAULT, _flags
from cerebras.pytorch.utils._micro_batch_size import MicroBatchSize
from cerebras.pytorch.utils.pol import POL


@dataclass
class _backends(_flags):
    """
    Backends configuration flags.

    Attributes:
        csx: CSX configuration flags
        DEFAULT: The sentinel value used to reset a flag back to its default value
    """

    DEFAULT = DEFAULT

    @dataclass
    class _csx(_flags):
        """
        CSX configuration flags.

        Attributes:
            precision: Precision configuration flags
            performance: Performance configuration flags
            debug: Debug configuration flags
        """

        @dataclass
        class _precision(_flags):
            """
            CSX precision configuration flags.

            Attributes:
                optimization_level: The precision optimization level (POL) to use
                    when compiling the model. The POL determines the level of
                    precision to use for the model's weights and activations and
                    can thus affect the model's accuracy and performance.
            """

            optimization_level: int = POL(default=1)

        @dataclass
        class _performance(_flags):
            """
            CSX performance configuration flags.

            Attributes:
                micro_batch_size: The micro-batch size to use when compiling the
                    model. The micro-batch size can affect the model's performance
                    and memory usage.

                    Valid values include:

                    * "auto": Automatically choose an optimal micro batch size.

                    * "explore": Search for an optimal micro batch size and return.

                    *
                      .. code:: python

                          {
                              "explore": {
                                  "min": Optional[<positive_int>],
                                  "max": Optional[<positive_int>]
                              }
                          }

                      Search for an optimal micro batch size within the min and
                      max bounds and return.

                    * <positive_int>: Use this micro batch size.

                    * None: Disable micro batch tiling.

                transfer_processes: The number of processes to use for transferring data
                    to and from the Wafer Scale Cluster.
            """

            micro_batch_size: MicroBatchSize.Type = MicroBatchSize(
                default="auto"
            )
            transfer_processes: int = 5

        @dataclass
        class _debug(_flags):
            """
            CSX debug configuration flags.

            Attributes:
                ini: INI configuration flags
                debug_args: Debug arguments to pass to the cluster
                drop_data: Whether to drop weight data if its not needed
                log_initialization: Whether to log initialization
                retrace_every_iteration: Whether to retrace the
                    training/validation graph every iteration
            """

            class INI(cerebras.appliance.utils.ini.INI):
                @property
                def _debug_args(self):
                    return backends.csx.debug.debug_args

            class INIDescriptor(Descriptor):
                def sanitize(self, value):
                    if isinstance(value, dict):
                        return self.default.__class__(**value)
                    return value

            ini: Union[INI, dict] = INIDescriptor(default=INI())

            class _DebugArgsDescriptor(DebugArgsDescriptor):
                def set_attr(self, obj, value):
                    if hasattr(obj, self._attr_name):
                        super().set_attr(obj, value)
                        # Only copy if backends has already been fully initialized
                        backends.csx.debug.ini.copy_from(
                            backends.csx.debug.debug_args
                        )
                    else:
                        super().set_attr(obj, value)

            debug_args: Union[DebugArgs, dict] = _DebugArgsDescriptor()

            drop_data: bool = DeviceConfig(default=False)
            lazy_initialization: bool = DeviceConfig(default=True)
            log_initialization: bool = True
            retrace_every_iteration: bool = RetraceEveryIteration(default=False)

            fabric_type_blacklist: Optional[
                List[Literal[FABRIC_TYPE_CS2, FABRIC_TYPE_CS3]]
            ] = None

            class MemoryLimit(Descriptor):
                """Descriptor for DebugArgs memory_limit."""

                def __init__(self, debug_arg_property):
                    super().__init__(default=None)
                    self.debug_arg_property = debug_arg_property

                def sanitize(self, value):
                    if value is not None:
                        getattr(
                            backends.csx.debug.debug_args.debug_usr,
                            self.debug_arg_property,
                        ).memory_bytes = (
                            value << 30
                        )  # gb to bytes conversion

                    return value

            compile_crd_memory_gi: Optional[int] = MemoryLimit(
                "compile_coord_resource"
            )
            execute_crd_memory_gi: Optional[int] = MemoryLimit(
                "execute_coord_resource"
            )
            wrk_memory_gi: Optional[int] = MemoryLimit("worker_resource")
            act_memory_gi: Optional[int] = MemoryLimit("activation_resource")
            cmd_memory_gi: Optional[int] = MemoryLimit("command_resource")
            wgt_memory_gi: Optional[int] = MemoryLimit("weight_resource")

        precision: _precision = _precision()
        performance: _performance = _performance()
        debug: _debug = _debug()

    csx: _csx = _csx()


backends: _backends = _backends()
