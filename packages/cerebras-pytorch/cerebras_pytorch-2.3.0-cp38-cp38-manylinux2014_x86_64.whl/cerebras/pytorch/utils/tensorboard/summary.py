# Copyright 2016-2023 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

"""Utility functions for writing scalars and tensors to event files"""

import logging
from typing import Union
from warnings import warn

import torch

from ...backend import current_backend_impl
from ..step_closures import step_closure


def summarize_scalar(name: str, scalar: Union[int, float, torch.Tensor]):
    """
    Save the scalar to the event file of the writer specified in the data
    executor

    Args:
        name: the key to save the scalar in the event file
        scalar: the scalar value to summarize.
            Note, if a torch.Tensor is provided, it must be a scalar tensor
            for which scalar.item() can be called
    """
    if not isinstance(scalar, (int, float, torch.Tensor)):
        raise TypeError(
            f"Expected int, float, or torch.Tensor for scalar summary "
            f"but got: {type(scalar)}"
        )

    if isinstance(scalar, (int, float)):
        backend = current_backend_impl(raise_exception=False)
        if backend and not backend.retrace_every_iteration:
            raise RuntimeError(
                "Passing a Python int or float scalar is not supported "
                "for the current backend. "
                "Only passing in a scalar torch.Tensor is supported"
            )

    if isinstance(scalar, torch.Tensor) and scalar.numel() != 1:
        raise ValueError(
            f"Expected tensor to be a scalar but tensor has size: "
            f"{scalar.size()}"
        )

    @step_closure
    def scalar_summary(name, writer, **kwargs):
        scalar = kwargs[name]
        if isinstance(scalar, torch.Tensor):
            scalar = scalar.item()

        writer.add_scalar(
            name, scalar, writer.base_step + backend.run_context.iteration
        )

    backend = current_backend_impl()
    writer = backend.run_context.writer

    if writer:
        scalar_summary(name, writer, **{name: scalar})
    else:
        logging.warning(
            f"Scalar summary for `{name}` was not saved as no SummaryWriter "
            f"was provided. "
        )
        warn(
            f"To enable writing scalar summaries, please pass in a "
            f"SummaryWriter object to the DataExecutor, e.g.\n\n"
            f"\twriter = cstorch.utils.tensorboard.SummaryWriter(...)"
            f"\texecutor = cstorch.utils.data.DataExecutor(..., writer=writer)"
        )


def summarize_tensor(name: str, tensor: torch.Tensor):
    """
    Save the tensor to the event file of the writer specified in the data
    executor

    Args:
        name: the key to save the tensor in the event file
        tensor: the torch.Tensor to summarize
    """
    if not isinstance(tensor, torch.Tensor):
        raise TypeError(
            f"Expected torch.Tensor for tensor summary but got: {type(tensor)}"
        )

    @step_closure
    def tensor_summary(name, writer, **kwargs):
        tensor = kwargs[name]
        writer.add_tensor(
            name,
            tensor.detach(),
            step=writer.base_step + backend.run_context.iteration,
        )

    backend = current_backend_impl()
    writer = backend.run_context.writer

    if writer:
        tensor_summary(name, writer, **{name: tensor})
    else:
        logging.warning(
            f"Tensor summary for `{name}` was not saved as no SummaryWriter "
            f"was provided. "
        )
        warn(
            f"To enable writing tensor summaries, please pass in a "
            f"SummaryWriter object to the DataExecutor, e.g.\n\n"
            f"\twriter = cstorch.utils.tensorboard.SummaryWriter(...)"
            f"\texecutor = cstorch.utils.data.DataExecutor(..., writer=writer)"
        )
