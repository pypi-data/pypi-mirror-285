# Copyright 2016-2023 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import fnmatch
import inspect
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from contextlib import nullcontext
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

import torch

import cerebras.pytorch as cstorch
from cerebras.appliance.log import ClassLogger, named_class_logger
from cerebras.appliance.utils.classes import retrieve_all_subclasses
from cerebras.pytorch.backend import current_backend_impl
from cerebras.pytorch.core.function_mode import (
    register_function_mode_forward_hook,
    register_function_mode_forward_pre_hook,
)
from cerebras.pytorch.utils.step_closures import RepeatStepClosure, step_closure


class BaseTensorListener(ABC):
    """Base tensor listener class."""

    def __init__(self):
        self.registry = None

        # Dictionary of captured tensors.
        self.tensors: Dict[str, torch.Tensor] = {}

    def __copy__(self):
        # default copy implementation.
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        # update unique listener fields.
        result.registry = None
        result.reset_state()
        return result

    def __deepcopy__(self, memo):
        # default deepcopy implementation.
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        # update unique listener fields.
        result.registry = None
        result.reset_state()
        return result

    @abstractmethod
    def match(self, tensor: torch.Tensor, name: str) -> bool:
        """
        Returns True if tensor needs to be captured.

        Args:
            tensor: tensor to capture.
            name: tensor name.
        """

    def on_tensor(self, tensor: torch.Tensor, name: str):
        """
        Implement this function to perform an action on each
        tensor that has been individually captured.
        To access tensor data, please use @cstorch.step_closure.

        Args:
            tensor: captured tensor.
            name: tensor name.
        """

    def on_all_tensors(self, tensors: Dict[str, torch.Tensor]):
        """
        Implement this function to perform an action on all
        tensor that has been captured during the model tracing.
        To access tensors data, please use @cstorch.step_closure.

        Args:
            tensors: dictionary where the key represents tensor
                name, and value represents corresponding tensor.
        """

    def _register_tensor(self, tensor: torch.Tensor, name: str):
        """
        Internal method to register captured tensor and apply instant hooks.

        Args:
            tensor: tensor to register inside listener.
            name: tensor name.
        """
        self.on_tensor(tensor, name)

        # Adding no-op to avoid inplace updates of the original tensor.
        self.tensors[name] = tensor.reshape(tensor.shape)

    def _on_batch_end(self):
        """Internal method to run post-step hooks."""
        backend = current_backend_impl()

        if (
            cstorch.backends.csx.debug.retrace_every_iteration
            or backend.run_context.is_initial_step
        ):
            self.on_all_tensors(self.tensors)

    def attach_registry(self, registry: Set[BaseTensorListener]):
        """Attach registry to the listener."""
        if self.registry is not None:
            raise RuntimeError(
                "TensorListener has already been attached to the registry. Please use copy(listener) to reuse it."
            )

        registry.add(self)
        self.registry = registry

    def reset_state(self):
        """
        Reset listener state between `step_fn` iterations.
        """
        self.tensors = {}


class NamedTensorListener(BaseTensorListener):
    """
    Base tensor listener class that implements
    tensor capturing by tensor name.
    """

    def __init__(
        self,
        listener_name: str,
        tensor_names: Union[str, list[str]],
    ):
        """
        Constructs named tensor listener.

        Args:
            listener_name: a listener name to be used in summarized tensor name.
            tensor_names: a list of tensor names to be captured. It also supports
                glob patterns to match group of tensors using pattern.
                See https://docs.python.org/3/library/fnmatch.html for more details.
        """
        super().__init__()

        self.listener_name = listener_name

        def arg_to_list(arg):
            res = arg or []
            return res if isinstance(res, list) else [res]

        self.tensor_names = arg_to_list(tensor_names)

    def save_tensor(self, tensor: torch.Tensor, name: str):
        """Save tensor summary."""
        from cerebras.pytorch.utils import tensorboard

        tensorboard.summarize_tensor(f"{self.listener_name}/{name}", tensor)

    def match(self, tensor: torch.Tensor, name: str):
        """Match tensor name using user-provided names."""
        return any(
            fnmatch.fnmatch(name, pattern) for pattern in self.tensor_names
        )

    def attach_registry(self, registry: Set[BaseTensorListener]):
        """Check for conflicts with existing listeners."""
        for listener in registry:
            if (
                isinstance(listener, NamedTensorListener)
                and listener.listener_name == self.listener_name
            ):
                raise RuntimeError(
                    f"TensorListener with the name \"{self.listener_name}\" is already registered. "
                    f"Please use a unique name for each listener to avoid conflicts."
                )
        super().attach_registry(registry)


class NormTensorListener(NamedTensorListener):
    """Tensor listener that computes tensor norms."""

    def on_tensor(self, tensor: torch.Tensor, name: str):
        """Calculate norm on for a single tensor."""
        self.save_tensor(torch.norm(tensor), name)

    def on_all_tensors(self, tensors: Dict[str, torch.Tensor]):
        """Calculate norm on for all captured tensors."""
        result = None
        for name, tensor in tensors.items():
            norm = torch.pow(torch.norm(tensor), 2.0)
            if result is None:
                result = norm
            else:
                result += norm

        if result is None:
            return

        self.save_tensor(torch.sqrt(result), "all")


class SummaryTensorListener(NamedTensorListener):
    """Tensor listener that summarizes every tensor."""

    def on_tensor(self, tensor: torch.Tensor, name: str):
        self.save_tensor(tensor, name)


def get_available_listeners():
    """
    Returns: dictionary of available tensor listener classes.
    """
    supported_listener_types = {}
    for cls in retrieve_all_subclasses(BaseTensorListener):
        if inspect.isabstract(cls):
            continue
        key = cls.__name__.lower().replace("tensorlistener", "")
        supported_listener_types[key] = cls
    return supported_listener_types


def create_listener(listener_type: str, **kwargs):
    """
    Construct a Listener object of the appropriate listener type.

    ``**kwargs`` are passed along to the TensorListener ``__init__``

    Args:
        listener_type: Type of listener to construct.
        kwargs: Passed along to the chosen listener type ``__init__``.
    """

    supported_listener_types = get_available_listeners()

    # Ensure we have a known listener.
    listener_opt_cls = supported_listener_types.get(listener_type)

    if not listener_opt_cls:
        raise ValueError(
            f"Unsupported listener type: {listener_type}. "
            f"Supported types: {list(supported_listener_types.keys())}"
        )

    return listener_opt_cls(
        **kwargs,
    )


@named_class_logger("ListenerMode")
class ListenerMode(ClassLogger):
    """
    ListenerMode class manages listeners execution using
    cerebras_pytorch function mode.
    """

    def __init__(self, listeners: Optional[List[BaseTensorListener]] = None):
        """
        Initialize listener mode with tensor listeners.

        Args:
            listeners: a list of tensor listener instances.
        """
        self.tensor_listeners: Set[BaseTensorListener] = set()

        if listeners is not None:
            for listener in listeners:
                self.add_listener(listener)

        self.all_tensor_names = []

        self.unique_tensor_names = None

    def add_listener(self, listener: BaseTensorListener) -> BaseTensorListener:
        """
        Register new tensor listener.

        Args:
            listener: a tensor listener instance.
        Returns: the same tensor listener instance attached to the
            listener mode registry.
        """
        listener.attach_registry(self.tensor_listeners)
        return listener

    def __enter__(self):
        # Reset listeners state before iteration.
        for listener in self.tensor_listeners:
            listener.reset_state()

        self.unique_tensor_names = defaultdict(int)

        # Reset captured names list.
        self.all_tensor_names = []

        def apply_listeners(arg: torch.Tensor, func_name: str):
            """Apply registered listeners for a given tensor."""
            backend = current_backend_impl()
            if (
                not isinstance(arg, torch.Tensor)
                or arg.device.type != backend.torch_device.type
            ):
                return arg

            scope_name = deepcopy(backend.current_scope_name)
            scope_name.scope_func = func_name

            name = str(scope_name)

            # In case we have the same operation called several times
            # within a module, the resulting tensors will have the same
            # name. So we make these tensor names unique by addind `.index`
            counter = self.unique_tensor_names[name]
            self.unique_tensor_names[name] += 1

            if counter:
                name = f"{name}.{counter}"

            # Uncomment to annotate tensors. For debug purposes only.
            # backend.set_attribute(arg, "tensor_name", name)

            self.all_tensor_names.append(name)

            for listener in self.tensor_listeners:
                if listener.match(arg, name):
                    listener._register_tensor(arg, name)

        def is_blacklisted_op(func):
            """Filter noisy ops."""
            # Avoid `__get__` like tensor accessors.
            if re.match(r"__[_a-zA-Z0-9]+__", func.__name__):
                return True
            # Skip annoying tensor movements and copy like ops.
            if func.__name__ in ["clone", "copy", "detach"]:
                return True
            return False

        def forward_pre_hook(func, types, args, kwargs):
            """
            Pre-forward function mode hook that hooks `grad_fn`
            in order to capture tensors from bwd pass.
            """
            if is_blacklisted_op(func):
                return

            def hook_bwd(tensor: torch.Tensor):
                if (
                    not isinstance(tensor, torch.Tensor)
                    or tensor.grad_fn is None
                    or not hasattr(tensor, '_func_name')
                ):
                    return None

                def set_grad_fn_hook(tensors, func_name):
                    backend = current_backend_impl()

                    def grad_fn_hook(bwd_tensor, func_name):
                        if (
                            not isinstance(bwd_tensor, torch.Tensor)
                            or bwd_tensor.device.type != backend.device.type
                            or hasattr(bwd_tensor, '_has_bwd_hook')
                        ):
                            return

                        apply_listeners(bwd_tensor, func_name)

                    torch.utils._pytree.tree_map(
                        lambda bwd_tensor: grad_fn_hook(bwd_tensor, func_name),
                        tensors,
                    )

                # Mark tensor to avoid multiple `grad_fn` registration for
                # the same tensor.
                if hasattr(tensor, '_has_bwd_hook'):
                    return

                tensor._has_bwd_hook = True

                tensor_func_name = tensor._func_name
                tensor.grad_fn.register_hook(
                    lambda inputs, outputs: set_grad_fn_hook(
                        inputs, tensor_func_name
                    )
                )

            torch.utils._pytree.tree_map(
                lambda arg: hook_bwd(arg), (args, kwargs)
            )

        self.fwd_pre_hook_handle = register_function_mode_forward_pre_hook(
            forward_pre_hook
        )

        def forward_hook(func, types, args, kwargs, res):
            """
            Post-forward function mode hook that applies listeners
            to the resulting tensors of fwd pass.
            """
            if is_blacklisted_op(func):
                return

            torch.utils._pytree.tree_map(
                lambda arg: apply_listeners(arg, func.__name__), res
            )

            def save_bwd_name(arg, func_name):
                if not isinstance(arg, torch.Tensor):
                    return
                arg._func_name = func_name

            # Annotate tensors with `_func_name` which is used
            # in `grad_fn` hooks for tensor naming.
            torch.utils._pytree.tree_map(
                lambda arg: save_bwd_name(arg, func.__name__), res
            )

        self.fwd_hook_handle = register_function_mode_forward_hook(forward_hook)

    def __exit__(self, *args, **kwargs):
        # Since we may run ListenerMode outside of step_fn,
        # so we have to use repeat step closure ctx to register
        # step closure function from listeners that are running
        # in the end of the batch step.
        backend = current_backend_impl()
        if cstorch.backends.csx.debug.retrace_every_iteration:
            ctx = nullcontext()
        else:
            ctx = RepeatStepClosure()

        with ctx:
            for listener in self.tensor_listeners:
                listener._on_batch_end()

        # Save all available tensor names to the file.
        @step_closure
        def save_tensor_names():
            # save available tensor names for capturing
            tensor_names_file = (
                Path(backend.data_executor.artifact_dir)
                / f"available_tensor_names.txt"
            )
            if not tensor_names_file.exists():
                with open(tensor_names_file, "w") as f:
                    f.write('\n'.join(sorted(self.all_tensor_names)))

        save_tensor_names()

        self.fwd_pre_hook_handle.remove()
        self.fwd_hook_handle.remove()
