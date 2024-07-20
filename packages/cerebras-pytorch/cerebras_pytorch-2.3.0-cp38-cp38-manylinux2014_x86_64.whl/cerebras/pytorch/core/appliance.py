# Copyright 2016-2023 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

"""Appliance Support For Pytorch"""
import functools
import itertools
import logging
import multiprocessing
import multiprocessing.dummy
import multiprocessing.pool
import os
import sys
import time
from collections import defaultdict
from contextlib import ExitStack
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

import dill
import grpc
import torch
from tqdm import tqdm

import cerebras.pytorch as cstorch
from cerebras.appliance.appliance_client import ApplianceClient
from cerebras.appliance.appliance_manager import (
    ApplianceManager,
    TensorGrouper,
    TensorTransferTracker,
)
from cerebras.appliance.cluster.client import ClusterManagementClient
from cerebras.appliance.cluster_config import ClusterConfig
from cerebras.appliance.errors import (
    ApplianceClientException,
    register_grpc_error_pickler,
)
from cerebras.appliance.pb.framework.appliance_service_pb2 import (
    CompileRequest,
    LoadRequest,
    RunInferenceRequest,
    RunRequest,
    SendCheckRequest,
)
from cerebras.appliance.pb.workflow.appliance.common.common_config_pb2 import (
    DebugArgs,
    FrameworkType,
)
from cerebras.appliance.pb.workflow.appliance.common.message_queue_pb2 import (
    ValidTopics,
)
from cerebras.appliance.pb.ws.cross_compile_state_pb2 import CrossCompileState
from cerebras.appliance.saver.h5_saver import hdf5_locking
from cerebras.appliance.utils import limit_mp_threads, short_temp_dir
from cerebras.pytorch import cerebras_pytorch_lib
from cerebras.pytorch.backend import current_backend_impl
from cerebras.pytorch.saver.checkpoint_reader import CheckpointReader
from cerebras.pytorch.saver.pt_h5_saver import PyTorchH5Saver
from cerebras.pytorch.saver.storage import (
    DeferredTensor,
    lazy_tensor_data_wrapper,
    saving_initial_state,
)
from cerebras.pytorch.utils.nest import serialize_visit_fns


class ApplianceMode(ApplianceManager):
    """Manage pytorch interactions with the appliance"""

    # pylint: disable=signature-differs
    def __init__(
        self,
        artifact_dir: str,
        compile_dir: str,
        cluster_config: ClusterConfig,
        checkpoint_reader_cls=CheckpointReader,
        op_profiler_config: Optional[LoadRequest.OpProfilerConfig] = None,
    ):
        super().__init__(
            config=deepcopy(cluster_config),
            debug_args=deepcopy(cstorch.backends.csx.debug.debug_args),
            compile_dir=Path(compile_dir),
            artifact_dir=Path(artifact_dir),
            framework_type=FrameworkType.PYTORCH,
            op_profiler_config=op_profiler_config,
        )

        self._last_fetched_iteration = 0
        self.output_names = []
        self.weight_names = {}
        self._output_name_to_idx = {}
        self.auxilliary_state_names = {}

        # Overwrite the number of transfer threads to be used for data transfer
        # using the global configuration flag
        self._transfer_threads = (
            cstorch.backends.csx.performance.transfer_processes
        )
        # Add fabric type blacklist to the management client arguments
        self._mgmt_client_args["fabric_type_blacklist"] = (
            cstorch.backends.csx.debug.fabric_type_blacklist
        )

        self.checkpoint_reader_cls = checkpoint_reader_cls
        self.tracker_execute = current_backend_impl().appliance_tracker

        # A set of rt tensor names that are sparsity masks.
        self._sparsity_mask_names = set()

        # Counter to track the initial checkpoint id.
        self._initial_ckpt_id = 0

        self._exec_prep_is_done = False

    def receive_activations(self, iteration: int):
        """Get activations from appliance.

        Args:
            iteration: Iteration to receive activations for. Note that
                activations are received sequentially. So, if this number is
                a few steps ahead of the last iteration that was received, then
                it counts from last fetched iteration up to this iteration, but
                only returns activations for the requested iteration.
        """
        for i in range(iteration, iteration + 1):
            activations = super().receive_activations(i)

            activation_map = dict()
            received_activations = dict()
            for name, tensor in activations.items():
                if name not in self._output_name_to_idx:
                    raise RuntimeError(
                        f"Received activation with name {name} at iteration {i}"
                        f", but no such name has been registered. Expected "
                        f"activation names are: "
                        f"{self._output_name_to_idx.values()}"
                    )
                activation = cstorch.from_numpy(tensor)
                activation_map[self._output_name_to_idx[name]] = activation
                received_activations[name] = activation

        self.tracker_execute.stop("recv_first_activation")
        self.tracker_execute.stop("execute_till_recv_loss")

        return received_activations

    def receive_output(self, iteration, name):
        out = super().receive_output(iteration, name)

        self.tracker_execute.stop("recv_first_activation")
        self.tracker_execute.stop("execute_till_recv_loss")

        return out

    def save_initial_state(self, initial_state_dict: dict) -> Union[str, None]:
        if not initial_state_dict:
            return None

        backend = current_backend_impl()

        initial_state_file = os.path.join(
            backend.device.device_data_dir,
            (
                f"initial_state_{self._initial_ckpt_id}.hdf5"
                if self._initial_ckpt_id
                else "initial_state.hdf5"
            ),
        )
        self._initial_ckpt_id += 1

        if os.path.exists(initial_state_file):
            raise FileExistsError(
                f"Initial checkpoint file {initial_state_file} already exists"
            )

        # After all weights were synced (computed) and available, we can
        # save them to the initial checkpoint.
        init_ckpt_dict = {}
        for name, weight in initial_state_dict.items():
            if isinstance(weight, cerebras_pytorch_lib.ApplianceInfo):
                # Special case to handle weights that needs to be carried over.
                init_ckpt_dict[name] = weight
            elif weight.is_tensor_available:
                try:
                    tensor = lazy_tensor_data_wrapper(weight)
                    if isinstance(tensor, DeferredTensor):
                        # Deferred tensors are created using `torch.empty()`
                        # which allocates virtual memory. But since the empty
                        # storage is never actually accessed in a defered
                        # tensor, we close that storage here to avoid spikes
                        # in virtual memory which may lead to OOM during fork.
                        cerebras_pytorch_lib.close_tensor_storage(tensor)

                    init_ckpt_dict[name] = tensor
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to get initial data for {name}"
                    ) from e
            else:
                raise RuntimeError(
                    f"Weight tensor \"{name}\" can not be saved to initial checkpoint as it is not available."
                )

        # We intermittently see HDF5 locking failures here. It's not clear what's
        # causing it, but given that `initial_state_file` is guaranteed to be unique
        # and only written to here, disabling file locking is ok.
        saver = PyTorchH5Saver()
        with cstorch.saver.storage.use_external_link(value=True), hdf5_locking(
            value=False
        ), saving_initial_state(value=True):
            saver.save(initial_state_file, init_ckpt_dict)

        del init_ckpt_dict

        return initial_state_file

    # pylint: disable=arguments-differ
    def compile(
        self,
        batch_size: int,
        cirh_str: str,
        cross_compile_state: Optional[CrossCompileState] = None,
        validate_only: bool = False,
    ):
        """
        Send a compile request to the coordinator
        """
        with self.tracker_execute.entry("compile"):
            with self.tracker_execute.entry("pt_cirh"):
                if validate_only:
                    logging.info("Compile validated locally")
                    return None

                compile_request = CompileRequest(
                    cirh_content=cirh_str,
                    compile_dir=str(self._compile_dir),
                    batch_size=batch_size,
                    num_csx=self.num_csx,
                    max_wgt_servers=self.max_wgt_servers,
                    num_workers_per_csx=self.num_workers_per_csx,
                    max_act_per_csx=self.max_act_per_csx,
                )
                if cross_compile_state is not None:
                    compile_request.cross_compile_state.CopyFrom(
                        cross_compile_state
                    )

            return super().compile(compile_request)

    def execute_prep(self, cleanup_stack: ExitStack):
        """Prepare for execution"""
        with self.tracker_execute.entry("execute_prep_details"):
            mgmt_client = cleanup_stack.enter_context(
                ClusterManagementClient(
                    tracker_execute=self.tracker_execute,
                    **self._mgmt_client_args,
                )
            )
            response = self.request_execute_job(mgmt_client, self._compile_resp)
            self.stage_execute_coordinator(response)

            cleanup_stack.enter_context(self.subscribe(ValidTopics.STALL))

            # From this point on, if we error out, we try to do a clean exit
            cleanup_stack.enter_context(
                self.clean_shutdown(mgmt_client, response['job_id'])
            )

        with self.tracker_execute.entry("execute_init_transfer_setup"):
            self.initialize_servers()

    def execute_session(
        self,
        initial_state_dict: Dict[str, Any] = None,
        appliance_weights: Dict[str, Any] = None,
        send_weights_grouper: Optional[TensorGrouper] = None,
        has_modified_seed: Optional[bool] = None,
    ):
        """Prepares weights and starts execution

        Args:
            initial_state_dict: Weights that needs to be sent to the appliance.
            appliance_weights: Weights that need to be carried over from PTR.
            send_weights_grouper: Callable to process TensorSendPayloads into TensorGroups
        """
        tensor_rt_groups = self.grpc_client.send_check(
            0, info_type=SendCheckRequest.InfoType.GROUP
        )

        rt_initial_state_dict = (
            {
                self._map_wgt_name_fw_to_rt(fw_name): (fw_name, weight)
                for fw_name, weight in initial_state_dict.items()
            }
            if initial_state_dict
            else {}
        )

        rt_appliance_weights = (
            {
                self._map_wgt_name_fw_to_rt(fw_name): (fw_name, info)
                for fw_name, info in appliance_weights.items()
            }
            if appliance_weights
            else {}
        )

        self._sparsity_mask_names = set()

        skipped_weights = set()

        for group in tensor_rt_groups:
            tensor_names = group.tensor_names
            if len(tensor_names) <= 1:
                continue

            # Make an assumption that first tensor in the group is a sparsity mask
            sparsity_mask, weights = tensor_names[0], tensor_names[1:]
            self._sparsity_mask_names.add(sparsity_mask)

            # Check if all tensors from the group are either in initial checkpoint or in the appliance,
            # otherwise, we need to send all tensors from the group to the appliance.
            if all(name in rt_initial_state_dict for name in tensor_names):
                continue

            if all(name in rt_appliance_weights for name in tensor_names):
                # We do not carry over sparsity mask if it wasn't changed.
                fw_name, _ = rt_appliance_weights[sparsity_mask]
                skipped_weights.add(fw_name)
                del rt_appliance_weights[sparsity_mask]
                continue

            for name in tensor_names:
                if name in rt_appliance_weights:
                    rt_initial_state_dict[name] = rt_appliance_weights[name]
                    del rt_appliance_weights[name]

        # Bake remaining apliances weights into initial_state_dict, so they can be
        # carried over to the next session.
        for rt_name, (fw_name, data) in rt_appliance_weights.items():
            rt_initial_state_dict[rt_name] = (
                fw_name,
                data.get_appliance_info(),
            )

        # The final dictionary that contains the weights that will be sent to the appliance
        # or carried over from the previous session.
        initial_weights = {
            fw_name: weight
            for fw_name, weight in rt_initial_state_dict.values()
        }

        out = super().execute_session(
            initial_weights,
            skipped_weights,
            send_weights_grouper,
            has_modified_seed,
        )

        # Update ApplianceInfo with InBuffer state after we sent/carried over
        # all the weight to the appliance.
        for data in (appliance_weights or {}).values():
            data.get_appliance_info().state = (
                cerebras_pytorch_lib.ApplianceInfoState.InBuffer
            )

        self._skipped_weights -= self._sparsity_mask_names
        return out

    def execute(
        self,
        run_request: RunRequest,
        cleanup_stack: ExitStack,
        initial_state_dict: Dict[str, Any] = None,
        appliance_weights: Dict[str, Any] = None,
        send_weights_grouper: Optional[TensorGrouper] = None,
        has_modified_seed: Optional[bool] = None,
    ):
        """Run a model on the appliance"""
        self.tracker_execute.start("execute_till_recv_loss")

        if not self._exec_prep_is_done:
            self.execute_prep(cleanup_stack)
            self._exec_prep_is_done = True

        with self.tracker_execute.entry("execute_init_transfer_setup"):
            self.initialize_session(
                run_request,
                self._compile_resp,
                has_modified_seed,
            )
            self.execute_session(
                initial_state_dict,
                appliance_weights,
                send_weights_grouper,
                has_modified_seed,
            )

        self.tracker_execute.start("recv_first_activation")

    def host_inference(
        self,
        host_request: RunInferenceRequest,
        checkpoint_filenames: List[str],
        cleanup_stack: ExitStack,
    ):
        """Host an inference model in the appliance"""

        self._inference_mode = True

        self.execute_prep(cleanup_stack)
        with self.tracker_execute.entry("execute_init_transfer_setup"):
            self.initialize_inference(
                host_request,
                self._compile_resp,
                drop_cmd_state=False,
            )
        if checkpoint_filenames:
            with self.tracker_execute.entry("execute_send_weights"):
                self.logger.info("About to send weights")
                self.send_weights_from_checkpoints(checkpoint_filenames)
                self.logger.info("Finished sending weights")
        with self.tracker_execute.entry("execute_start_streaming"):
            self.logger.info("Finalizing appliance staging for the run")
            self.start_streaming()
            self.logger.info("Appliance staging is complete")

    def infer(self, prompt: List[int]) -> Generator[int, None, None]:
        """
        Submit the given prompt to the currently loaded inference model and
        yield tokens as they are generated.

        Args:
            prompt: tokens of the prompt to seed generation
        """
        yield from self._grpc_client.infer(prompt)

    def move_to_ptr(self, tensor_name: str, tensor_id: int) -> None:
        """Move a tensor to PTR which makes is available for the next session."""
        rt_name = self._map_wgt_name_fw_to_rt(tensor_name)
        return super().move_to_ptr(rt_name, tensor_id)

    def get_from_ptr(
        self, name: str, tensor_id: int, keep_in_repo: bool = False
    ):
        """Get a tensor from PTR."""
        return super().get_from_ptr(tensor_id, keep_in_repo)

    def construct_debug_args(self) -> DebugArgs:
        debug_args = super().construct_debug_args()

        # Populate the visit_fn_map in the debug_args so that they
        # can be propagated to the workers
        for (
            serialized_types,
            serialized_visit_fn,
        ) in serialize_visit_fns().items():
            debug_args.debug_wrk.visit_fn_map[serialized_types] = (
                serialized_visit_fn
            )

        return debug_args

    def compute_compile_hash(
        self,
        cirh_str: str,
        batch_size: int,
        cross_compile_state: CrossCompileState,
    ):
        """
        Compute the hash for the compile request. When modifying this function,
        please make sure that the hashing logic is in sync with logic in CRD.
        Note that the purpose of this function is to define a compile hash
        which is going to be used only locally (within this process), so we
        doesn't include static information (like fabric info, release id, etc.)
        to compute the hash.
        """
        checksum = [
            cirh_str,
            self._debug_args.debug_crd.stop_compile_at,
            self._debug_args.debug_crd.autogen_policy,
            self._debug_args.debug_crd.numeric_config,
            self._debug_args.debug_crd.disable_ws_incremental_compile,
            self._debug_args.debug_crd.disable_autogen_leftover_conversion,
            self.num_csx,
            batch_size,
            self.max_wgt_servers,
            self.max_act_per_csx,
            cross_compile_state,
        ]
        return hash("".join([str(item) for item in checksum]))

    @property
    def _checkpoint_reader_cls(self):
        return self.checkpoint_reader_cls

    def _map_wgt_name_fw_to_rt(self, tensor_name):
        if tensor_name in self.weight_names:
            return self.weight_names[tensor_name]
        if tensor_name in self.auxilliary_state_names:
            return self.auxilliary_state_names[tensor_name]
        return tensor_name

    def save_weights(
        self,
        weights: List[Tuple[str, Union[torch.Tensor, Any]]],
        file_name: str,
        iteration: int,
        fetch_only: bool = False,
    ) -> None:
        """Request weights from appliance and save to the file_name.

        Args:
            weights: List of weights to save. Each weight is a tuple of the
                weight name and the tensor (or other objects) to fetch from
                the appliance and save.
            file_name: Name of the file to save the weights to.
            iteration: Appliance iteration number to save the weights for.
            fetch_only: If True, forces weights fetching from the appliance.
        """

        def get_parameter_name(tensor):
            if (
                isinstance(tensor, torch.Tensor)
                and tensor.device.type == "lazy"
            ):
                # pylint: disable=c-extension-no-member
                # pylint: disable=no-member
                return cerebras_pytorch_lib.get_tensor_name(tensor)
            return getattr(tensor, "_parameter_name", None)

        def get_tensors():
            seen_weights = set()

            # Create a map between the weight name and the external name
            # to handle duplicate weights
            alias_map = defaultdict(list)
            for external_name, obj in weights:
                parameter_name = get_parameter_name(obj)
                if parameter_name is not None:
                    # pylint: disable=protected-access
                    alias_map[parameter_name].append(external_name)

            # external_name: The name seen by the user (what's saved in ckpt)
            # weight_name: The name of the weight in the model
            # tensor_name: The name of the weight seen by the appliance
            for external_name, obj in weights:
                ckpt_indices = [external_name]

                weight_name = get_parameter_name(obj)
                if weight_name is not None:
                    ckpt_indices.extend(
                        alias
                        for alias in alias_map[weight_name]
                        if alias != external_name
                    )
                else:
                    weight_name = external_name

                if weight_name in seen_weights:
                    continue
                else:
                    seen_weights.add(weight_name)

                tensor_name = None

                if isinstance(obj, torch.Tensor):
                    tensor_name = self.weight_names.get(weight_name)

                    if weight_name in self.skipped_weights:
                        logging.debug(f"Not fetching skipped: {weight_name}")
                        if obj.device.type == "lazy":
                            obj = lazy_tensor_data_wrapper(obj)
                        tensor_name = None
                    elif tensor_name is None and obj.device.type == "lazy":
                        tensor_name = weight_name

                    if tensor_name is None:
                        logging.debug(
                            f"Saving tensor {external_name} to indices: {ckpt_indices}"
                        )
                        # Save the object as is
                        yield None, ckpt_indices, obj
                    else:
                        logging.debug(
                            f"Fetching {tensor_name} and saving to indices: {ckpt_indices}"
                        )
                        # Fetch tensor before saving
                        yield tensor_name, ckpt_indices, None
                elif fetch_only:
                    logging.debug(
                        f"Fetching {weight_name} and saving to indices: {ckpt_indices}"
                    )
                    # Fetch tensor before saving
                    yield weight_name, ckpt_indices, None
                else:
                    logging.debug(
                        f"Saving object {external_name} to indices: {ckpt_indices}"
                    )
                    # Save the object as is
                    yield None, ckpt_indices, obj

        recv_tensors = list(get_tensors())

        # Build unique tensor names for validating.
        recv_tensor_names = {name for name, _, _ in recv_tensors}

        # Some related tensors should be requested together to minimize peak
        # memory. Each tensor is independent from the other tensors; the
        # grouping is just to control the fetch order.
        recv_groups = []

        # self.recv_groups is a (possibly empty) list of list of tensor names.
        if self.recv_groups:
            # Build a lookup from tensor_name->(tensor_name, indices, obj)
            # the `None` key will have overlaps, but thats fine. All tensors
            # with a name are guaranteed unique.
            recv_tensor_dict = {t[0]: t for t in recv_tensors}

            # For each group of tensor names, build a matching "group" of
            # recv_tensor input (tuples of (name, indices, obj) )
            for group in self.recv_groups:
                recv_group = []
                for tensor_name in group:
                    inputs = recv_tensor_dict.get(tensor_name, None)
                    if inputs is not None:
                        # Move from global recv list to this group.
                        recv_tensors.remove(inputs)
                        recv_group.append(inputs)
                recv_groups.append(recv_group)

        # Each remaining tensor (maybe all of them) is its own group.
        recv_groups.extend([t] for t in recv_tensors)

        transfer_tracker = TensorTransferTracker()

        with self.tracker_execute.entry(
            "Retrieve and Save weights"
        ), limit_mp_threads():
            if self._transfer_threads > 1:
                ctx = multiprocessing.get_context('spawn')
                pool_cls = functools.partial(
                    multiprocessing.pool.Pool,
                    context=ctx,
                )
            else:
                ctx = multiprocessing.get_context()
                pool_cls = multiprocessing.dummy.Pool
            with short_temp_dir():
                m = ctx.Manager()
            lock = m.Lock()
            with cstorch.saver.storage.use_cstorch_types(True), pool_cls(
                processes=self._transfer_threads,
                initializer=WeightReceiver.initializer,
                initargs=(
                    self._coord_address,
                    self._certificate_bytes,
                    self._default_authority,
                    file_name,
                    iteration,
                    lock,
                ),
            ) as pool:
                try:
                    iter_recv = itertools.chain.from_iterable(
                        pool.imap_unordered(WeightReceiver.runner, recv_groups)
                    )
                    for pkl in tqdm(
                        iter_recv,
                        total=len(recv_tensor_names),
                        desc="Transferring weights from server",
                        dynamic_ncols=True,  # Match console width
                        unit=" tensors",
                        file=sys.stdout,
                        disable=None,  # Disable on non-TTY
                    ):
                        tensor_name, outcome = WeightReceiver.deserialize(pkl)
                        transfer_tracker.add(tensor_name, outcome)
                except ApplianceClientException as ex:
                    raise ex

            transfer_tracker.validate(recv_tensor_names)


class WeightReceiver:
    """A class to use in a multiprocessing context for receiving weights."""

    impl: Optional["WeightReceiver"] = None

    def __init__(
        self,
        coord_address,
        certificate_bytes: Optional[bytes],
        default_authority,
        file_name,
        iteration,
        lock,
    ):
        """Constructs a `WeightReceiver` instance.

        Args:
            coord_address: Address of the coordinator to send to.
            certificate_bytes: Optional PEM encoded certificate byte string for
                grpc secure channel setup.
            default_authority: Authority to authorize communication.
        """
        credentials = None
        if certificate_bytes:
            credentials = grpc.ssl_channel_credentials(certificate_bytes)

        self._grpc_client = ApplianceClient(
            coord_address,
            credentials=credentials,
            default_authority=default_authority,
        )

        self._file_name = file_name
        self._iteration = iteration
        self._writer_lock = lock

        # Add pickling support to exceptions so that they include their
        # traceback
        from tblib import pickling_support

        pickling_support.install()

        # gRPC exceptions are not picklable by default. Register custom picklers
        # so they can be properly pickled to be sent across processes.
        register_grpc_error_pickler()

    def __call__(self, inputs):
        """Downloads the given tensor through gRPC from appliance service."""
        tensor_name = "Unknown"
        ckpt_indices = []
        try:
            tensor_name, ckpt_indices, tensor = inputs
            if tensor_name is not None:
                tensor = self._grpc_client.recv_output(
                    self._iteration, tensor_name
                )

                try:
                    # Make the tensor writable so that we don't have to copy it
                    # in `cstorch.from_numpy()`. Some arrays cannot be modified
                    # so we ignore the error and copy the array instead.
                    tensor.flags.writeable = True
                except Exception:  # pylint: disable=broad-except
                    pass

                tensor = cstorch.from_numpy(tensor)
            with self._writer_lock, hdf5_locking(value=False):
                saver = PyTorchH5Saver()

                def retry(f, *args):
                    attempts = 3
                    delay = 1
                    while attempts:
                        try:
                            return f(*args)
                        except OSError:
                            attempts -= 1
                            if not attempts:
                                raise
                            logging.warning(
                                f"Will retry {f} {attempts} in {delay} seconds",
                                exc_info=True,
                            )
                            time.sleep(delay)
                            delay *= 2

                retry(
                    saver.save_tensor, self._file_name, ckpt_indices[0], tensor
                )

                retry(
                    saver.create_links,
                    self._file_name,
                    ckpt_indices[0],
                    ckpt_indices[1:],
                )

            return WeightReceiver.serialize((tensor_name, True))
        except Exception as e:  # pylint: disable=broad-except
            return WeightReceiver.serialize((tensor_name, e))

    @staticmethod
    def serialize(val):
        """Generic serialization using dill."""
        return dill.dumps(val)

    @staticmethod
    def deserialize(pkl_val):
        """Generic de-serialization method using dill."""
        return dill.loads(pkl_val)

    @staticmethod
    def initializer(*args, **kwargs):
        """The initializer to use in multiprocessing."""
        WeightReceiver.impl = WeightReceiver(*args, **kwargs)

    @staticmethod
    def runner(group):
        """The runner method to use in multiprocessing."""
        assert WeightReceiver is not None, "Initializer must be called."
        # pylint: disable=not-callable
        return [WeightReceiver.impl(inputs) for inputs in group]
