# Copyright 2016-2023 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

"""The executor used to configure the run."""
import copy
from contextlib import ExitStack, nullcontext
from pathlib import Path
from threading import Event
from typing import Dict, List, Literal, Optional, Type, Union
from warnings import warn

import numpy as np

import cerebras.pytorch as cstorch
from cerebras.appliance.CSConfig import CSConfig
from cerebras.appliance.log import ClassLogger, named_class_logger
from cerebras.appliance.utils.file import create_symlink
from cerebras.pytorch.backend import current_backend_impl
from cerebras.pytorch.experimental.listener import (
    BaseTensorListener,
    ListenerMode,
)
from cerebras.pytorch.profiler import ProfilerRegistry
from cerebras.pytorch.utils.data.utils import Schedule
from cerebras.pytorch.utils.utils import UNSPECIFIED

from ..profiler import Activity, Profiler
from .dataloader import DataLoader

# Type hint for micro_batch_size settings
MbsSetting = Union[
    None, int, Literal["explore", "auto"], Dict[str, Dict[str, int]]
]


@named_class_logger
class DataExecutor(ClassLogger):
    """Defines a single execution run on a Cerebras wafer scale cluster."""

    # pylint: disable=super-init-not-called
    def __init__(
        self,
        dataloader: DataLoader,
        num_steps: Optional[int] = None,
        checkpoint_steps: Union[int, Schedule, None] = None,
        activation_steps: Optional[int] = None,
        cs_config: Optional[CSConfig] = UNSPECIFIED,
        writer: Optional["SummaryWriter"] = UNSPECIFIED,
        profiler_activities: Optional[List[Type[Activity]]] = None,
        listeners: Optional[List[BaseTensorListener]] = UNSPECIFIED,
        micro_batch_size: MbsSetting = UNSPECIFIED,
    ):
        """
        Args:
            dataloader: the dataloader to use for the run
            num_steps: the number of steps to run. Defaults to 1 if the backend
                was configured for compile or validate only
            checkpoint_steps: Checkpoint cadence. This can be:
                - None: To disable checkpointing. This is the default.
                - int: To take checkpoints at this frequency and at `num_steps`.
                - Schedule: To take checkpoints at the given arbitrary schedule. Note that when
                    using a schedule object, the intervals must be zero-indexed.
            activation_steps: the interval at which to schedule fetching
                activations from the cluster
            cs_config: (DEPRECATED) An optional CSConfig object
            writer: (DEPRECATED) The summary writer to be used to write any summarized
                scalars or tensors to tensorboard
            profiler_activities: The list of activities to profile.
                By default the total samples, the client side rate and global
                rate are tracked and accessible via the profiler attribute.
            micro_batch_size: (DEPRECATED) Can be one of "auto", "explore", or an int
                representing the micro batch size that the Cerebras compiler should use.
                Only applicable in CSX runs.
        """
        self.dataloader = dataloader

        self.backend = current_backend_impl()

        if listeners is not UNSPECIFIED:
            warn(
                "Passing listeners to the DataExecutor is deprecated. "
                "Please use the listener API directly:\n\n"
                "\tlistener_mode = cstorch.experimental.listeners.ListenerMode(listeners)\n"
                "\tfor batch in data_executor:\n"
                "\t\twith listener_mode:\n"
                "\t\t\t...\n\n"
            )
            self.listener_mode = ListenerMode(listeners)
        else:
            self.listener_mode = nullcontext()

        self.op_profiler_config = None
        self._artifact_dir: Optional[Path] = None

        if cs_config is not UNSPECIFIED and cs_config is not None:
            warn(
                "Passing cs_config to the DataExecutor is deprecated. "
                "Please pass in a cstorch.distributed.ClusterConfig instance "
                "to the backend constructor instead. For example,\n\n"
                "\tbackend = cstorch.backend(\n"
                "\t\t\"CSX\", cluster_config=cstorch.distributed.ClusterConfig(...)\n"
                "\t)"
            )
            if not isinstance(cs_config, CSConfig):
                raise TypeError(
                    f"Expected cs_config to be of type cstorch.utils.CSConfig, "
                    f"but got {type(cs_config)}."
                )

            from dataclasses import fields

            from cerebras.appliance.cluster_config import ClusterConfig

            cstorch.backends.csx.performance.transfer_processes = (
                cs_config.transfer_processes
            )
            cstorch.backends.csx.precision.optimization_level = (
                cs_config.precision_opt_level
            )
            cstorch.backends.csx.debug.debug_args = cs_config.debug_args
            cstorch.backends.csx.debug.fabric_type_blacklist = (
                cs_config.fabric_type_blacklist
            )

            cluster_config = {
                field.name: value
                for field in fields(ClusterConfig)
                if (value := getattr(cs_config, field.name, None))
            }

            self.logger.debug(f"ClusterConfig: {cluster_config}")
            self.backend.cluster_config = ClusterConfig(**cluster_config)
            # pylint: disable=protected-access
            self.backend.cluster_config._workflow_id = cs_config.workflow_id

        if writer is not UNSPECIFIED:
            warn(
                "Passing writer to the DataExecutor is deprecated. "
                "Please create and write to the SummaryWriter directly. "
            )

            from cerebras.pytorch.utils import tensorboard

            if writer is not None and not isinstance(
                writer, tensorboard.SummaryWriter
            ):
                raise TypeError(
                    f"Expected writer to be a "
                    f"cstorch.utils.tensorboard.SummaryWriter object. "
                    f"Got: {type(writer)}"
                )
        else:
            writer = None

        if not self.backend.is_e2e_execution:
            if num_steps and num_steps > 1:
                self.logger.warning(
                    "Specified num_steps > 1 when backend was configured "
                    "for compile/validate only. Setting num_steps to 1."
                )
            num_steps = 1
        elif num_steps is None:
            # If num_steps is not specified, we will try to infer the number of
            # steps from the dataloader.
            try:
                num_steps = len(dataloader)
            except TypeError:
                # Dataset length is not known
                raise RuntimeError(
                    "Could not infer the number of steps as the length of the "
                    "dataloader is not known. Please provide num_steps to the data executor"
                )
        elif num_steps < 1:
            raise RuntimeError(f"Expected num_steps >= 1, but got {num_steps}.")

        if micro_batch_size is not UNSPECIFIED:
            warn(
                f"Setting micro_batch_size via the DataExecutor is deprecated. "
                f"Please set cstorch.backends.csx.performance.micro_batch_size "
                f"= {micro_batch_size}"
            )
            if self.backend.is_csx:
                cstorch.backends.csx.performance.micro_batch_size = (
                    micro_batch_size
                )

                if (
                    cstorch.backends.csx.performance.micro_batch_size
                    == "explore"
                    and not self.backend.compile_only
                ):
                    raise ValueError(
                        "Setting micro_batch_size == 'explore' is only "
                        "supported in compile_only mode."
                    )
            elif micro_batch_size is not None:
                raise ValueError(
                    "`micro_batch_size` is a valid option only for the CSX backend."
                )

        op_profiler = ProfilerRegistry.get_profiler()
        # For the models authored by the user, op_profiler_config would be
        # None, if profiling was not asked for.
        if op_profiler is not None:
            self.op_profiler_config = op_profiler.configure_profiler(
                self.backend.is_csx, num_steps
            )

        def check_steps(name, value, lowerbound):
            if value is not None:
                if not isinstance(value, int):
                    raise TypeError(
                        f"Expected {name} to be have \"int\" or \"None\" type. "
                        f"Got: \"{type(activation_steps)}\""
                    )
                if not (
                    value >= lowerbound
                ):  # pylint: disable=superfluous-parens
                    raise RuntimeError(
                        f"Expected {name} to be an integer >= {lowerbound} or \"None\". "
                        f"Got: {value}"
                    )

        # Validate steps parameters
        check_steps("activation_steps", activation_steps, 1)
        activation_steps = activation_steps or 1
        activation_steps = min(num_steps, activation_steps)

        if isinstance(checkpoint_steps, int):
            check_steps("checkpoint_steps", checkpoint_steps, 0)

            # Sync activation steps with checkpoint steps.
            if checkpoint_steps:
                checkpoint_steps = Schedule(
                    [
                        Schedule.Range(
                            start=min(checkpoint_steps - 1, num_steps - 1),
                            end=num_steps,
                            step=checkpoint_steps,
                            include_last=True,
                        )
                    ]
                )
            else:
                checkpoint_steps = Schedule([])

        if isinstance(checkpoint_steps, Schedule):
            checkpoint_schedule = copy.deepcopy(checkpoint_steps)

            aligned_activation_steps = np.gcd.reduce(
                [activation_steps]
                + [
                    step + 1
                    for range in checkpoint_schedule.range()
                    for step in range
                ]
            )

            if aligned_activation_steps != activation_steps:
                self.logger.warning(
                    f"Activation frequency was reduced from {activation_steps} to "
                    f"{aligned_activation_steps} because of the checkpoint schedule. "
                    f"This is because some activations may be accessed at any of "
                    f"the checkpoint steps {tuple(checkpoint_schedule.range())}. "
                    f"To avoid the reduction make sure that activation steps are "
                    f"divisible by all checkpoint steps."
                )
                activation_steps = aligned_activation_steps

        elif checkpoint_steps is None:
            checkpoint_schedule = Schedule([])
        else:
            raise ValueError(
                f"checkpoint_steps must be None, integer, or a Schedule, "
                f"but got {checkpoint_steps}."
            )

        self.run_context = RunContext(
            dataloader,
            num_steps,
            checkpoint_schedule,
            activation_steps,
            writer,
            profiler_activities,
        )

    def __len__(self) -> int:
        return len(self.run_context)

    @property
    def iteration(self) -> int:
        """Returns the current 0-indexed step that the executor is on."""
        return self.run_context.iteration

    @property
    def user_iteration(self) -> int:
        """Returns the current 1-indexed step that the executor is on."""
        return self.run_context.user_iteration

    @property
    def on_final_iteration(self) -> bool:
        """Returns whether the executor is on the final step."""
        return self.run_context.is_final_step

    @property
    def profiler(self) -> Optional[Profiler]:
        """Returns the profiler object, if it exists."""
        return self.run_context.profiler

    @property
    def writer(self) -> Optional["SummaryWriter"]:
        """Returns the writer object, if it exists."""
        return self.run_context.writer

    @property
    def cs_config(self):
        """Raises an error if the cs_config is accessed."""
        raise RuntimeError(
            "The DataExecutor no longer owns a CSConfig object. "
            "Please access the ClusterConfig object from the backend instead. "
            "i.e. cstorch.backend().cluster_config"
        )

    @property
    def artifact_dir(self) -> Path:
        """Returns the artifact directory of the executor."""
        if self._artifact_dir is None:
            raise RuntimeError(
                "DataExecutor must be iterated before having an artifact directory."
            )
        return self._artifact_dir

    def _setup_artifact_dir(self):
        """Sets up the artifact directory of this executor."""

        def _get_executor_dir(name) -> Path:
            if isinstance(name, int):
                name = f"{name:06d}"
            return Path(self.backend.artifact_dir) / "executors" / name

        self.backend.executor_counter += 1
        self._artifact_dir = _get_executor_dir(self.backend.executor_counter)
        self._artifact_dir.mkdir(parents=True, exist_ok=True)

        latest_symlink = _get_executor_dir("latest")
        create_symlink(
            latest_symlink,
            Path(self._artifact_dir).relative_to(latest_symlink.parent),
        )

    def __enter__(self):
        self._setup_artifact_dir()
        self.backend.data_executor_stack.append(self)
        self.backend.register_dataloader(self.dataloader)
        self.run_context.__enter__()

    def __exit__(self, *args):
        self.run_context.__exit__(*args)
        self.backend.data_executor_stack.pop()

    def __iter__(self):
        with self:

            def get_batches():
                while True:
                    iterable = iter(self.dataloader)
                    try:
                        batch = next(iterable)
                    except StopIteration:
                        raise RuntimeError(
                            "Iterating the dataloader did not return any values. "
                            "This is possibly because the dataset is too small "
                            "for the specified batch_size or drop_last settings. "
                            "Please make sure that the dataloader is able to generate "
                            "at least one batch."
                        )

                    yield batch

                    if self.backend.backend_type.is_csx:
                        while True:
                            yield batch

                    try:
                        while True:
                            yield next(iterable)
                    except StopIteration:
                        # If the iterable is exhausted, we need to start again
                        pass

            for _step, batch in zip(self.run_context, get_batches()):
                with self.listener_mode:
                    yield self.backend.on_batch_start(batch)
                self.backend.on_batch_end()


def current_executor() -> DataExecutor:
    """Returns current data executor."""
    return current_backend_impl().data_executor


class RunContext:
    """Defines a single run of the appliance."""

    def __init__(
        self,
        dataloader: DataLoader,
        num_steps: int,
        checkpoint_schedule: Schedule,
        activation_steps: int,
        writer: Optional["SummaryWriter"] = None,
        profiler_activities: Optional[List[Type[Activity]]] = None,
    ):
        self.backend = current_backend_impl()

        if not isinstance(dataloader, DataLoader):
            raise TypeError(
                "Detected that dataloader was not wrapped using a "
                "cstorch.utils.data.DataLoader.\n"
                "Please wrap your dataloader in a Cerebras Dataloader:\n\n"
                "\tdataloader = cstorch.utils.data.DataLoader(input_fn, ...)\n\n"
                "where `input_fn` is a callable that returns a PyTorch dataloader. "
                "For more details, please see the documentation for "
                "cstorch.utils.data.DataLoader."
            )

        self.dataloader = dataloader
        self.num_steps = num_steps
        self.checkpoint_schedule = checkpoint_schedule
        self.activation_steps = activation_steps

        # Event that keeps track of whether tracing has occurred
        self.traced = Event()

        self.writer = writer

        self.step = -1
        self.cleanup_stack = None

        self.profiler: Optional[Profiler] = None
        self.profiler_activities = profiler_activities

    @property
    def is_pre_initial_step(self) -> bool:
        """Returns true if the current step less than zero."""
        return self.step < 0

    @property
    def is_initial_step(self) -> bool:
        """Returns true if the current step is zero."""
        return self.step == 0

    @property
    def is_final_step(self) -> bool:
        """Returns true if the current step is the final step."""
        return self.user_iteration >= self.num_steps

    @property
    def is_checkpoint_step(self) -> bool:
        """Returns true if the current step is a checkpoint step."""
        return self.checkpoint_schedule.match(self.step)

    @property
    def is_activation_step(self) -> bool:
        """Returns true if the current step is an activation step.

        Technically when iteration = 0 the condition iteration % freq == 0 is true, however on the
        appliance side the activation is not available. To have correct iteration indexing we need
        to check that user_iteration % activation_steps == 0, where user_itaration = iteration + 1,
        otherwise in case we have 4 iterations [0, 1, 2, 3] and activation_steps = 2 we will get
        only one activation from the iteration=2, however we should return activations from
        iterations [1, 3].
        """
        assert self.activation_steps > 0  # Already validated in the constructor
        return (
            self.user_iteration % self.activation_steps == 0
            or self.is_final_step
        )

    @property
    def iteration(self) -> int:
        """Returns current step."""
        return self.step

    @property
    def user_iteration(self) -> int:
        """Returns user facing iteration number."""
        return self.step + 1

    def __len__(self) -> int:
        return self.num_steps

    def __enter__(self):
        self.step = -1  # set step < 0 before the run starts
        self.backend.on_run_start()
        self.step = 0  # set step to 0 as we enter the context
        self.traced.clear()
        self.cleanup_stack = ExitStack()
        self.cleanup_stack.__enter__()

        if self.backend.is_e2e_execution:
            self.profiler = Profiler(
                outdir=self.backend.data_executor.artifact_dir,
                activities=self.profiler_activities,
            )
            self.profiler.__enter__()

    def __exit__(self, *args):
        self.cleanup_stack.__exit__(*args)
        self.backend.on_run_end(*args)
        self.cleanup_stack = None

        if self.profiler is not None:
            self.profiler.__exit__(*args)

    def __iter__(self):
        # sanity check as the user should never use RunContext directly
        assert self.cleanup_stack is not None

        while self.step < self.num_steps:
            yield self.step
            self.step += 1
