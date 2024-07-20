"""Cerebras specific functional op implementations."""

# Copyright 2016-2023 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

import torch

import cerebras.pytorch as cstorch
from cerebras.appliance import logger


def one_hot(array, num_classes):
    """Cerebras specific implementation of one_hot"""
    if num_classes == -1:
        logger.error("num_class argument to one_hot cannot be -1")
    init = torch.zeros(
        array.shape + (num_classes,), device=array.device, dtype=torch.int
    )
    res = init.scatter_(-1, array.unsqueeze(-1), 1)
    return res


# CIRH ScopeBoundary op boundary_type enum
BEGIN_FORWARD = 'BEGIN_FORWARD'
BEGIN_BACKWARD = 'BEGIN_BACKWARD'
END_FORWARD = 'END_FORWARD'
END_BACKWARD = 'END_BACKWARD'


def scope_boundary(input, boundary_type, scope_name):
    """
    This function is used to set a boundary after input, or place the cirh.ScopeBoundary op
    after `input` in the CIRH graph.

    Args:
        boundary_type (str): The type of the boundary. One of `BEGIN_FORWARD`, 'BEGIN_BACKWARD',
            'END_FORWARD`, or `END_BACKWARD`.
        scope_name (str): The name of the scope.
    """

    if cstorch.use_cs():
        from cerebras.pytorch import cirh

        return cirh.ScopeBoundary(
            input,
            boundary_type=boundary_type,
            scope_name=scope_name,
        )
    return input


def enter_scope(input, scope_name):
    """
    This module is used as a wrapper function of 'EnterFunction' autograd functions,
    which can set the "BEGIN" boundaries in CIRH graph.
    """
    return EnterFunction.apply(input, scope_name)


def exit_scope(input, scope_name):
    """
    This module is used as a wrapper function of 'ExitFunction' autograd functions,
    which can set the "END" boundaries in CIRH graph.
    """
    return ExitFunction.apply(input, scope_name)


class EnterFunction(torch.autograd.Function):
    """
    This module is used to set a boundary after 'input'. In the foward pass, the type of
    boundary is BEGIN_FORWARD. In the backward, the type of boundary is END_BACKWARD.

    `scope_boundary()` is used to invoke the custom call to generate cirh.ScopeBoundary.
    """

    @staticmethod
    def forward(ctx, input, scope_name):
        ctx.scope_name = scope_name
        return scope_boundary(input, BEGIN_FORWARD, scope_name)

    @staticmethod
    def backward(ctx, grad_output):
        return (
            scope_boundary(grad_output, END_BACKWARD, ctx.scope_name),
            None,
            None,
        )


class ExitFunction(torch.autograd.Function):
    """
    This module is used to set a boundary after 'input'. In the foward pass, the type of
    boundary is END_FORWARD. In the backward, the type of boundary is BEGIN_BACKWARD.

    `scope_boundary()` is used to invoke the custom call to generate cirh.ScopeBoundary.
    """

    @staticmethod
    def forward(ctx, input, scope_name):
        ctx.scope_name = scope_name
        return scope_boundary(input, END_FORWARD, scope_name)

    @staticmethod
    def backward(ctx, grad_output):
        return (
            scope_boundary(grad_output, BEGIN_BACKWARD, ctx.scope_name),
            None,
            None,
        )


class CSXSparseMatMul(torch.autograd.Function):
    """CSX SparseMatMul Op."""

    @staticmethod
    def forward(ctx, input_values, input_indices, weight):
        ctx.save_for_backward(input_values, input_indices, weight)
        return cstorch.cirh.SparseMatMul(input_values, input_indices, weight)

    @staticmethod
    def backward(ctx, grad_output):
        grad_input_values, grad_weight = cstorch.cirh.SparseMatMulGrad(
            grad_output, *ctx.saved_tensors
        )
        grad_input_indices = None

        return grad_input_values, grad_input_indices, grad_weight


def sparse_matmul(
    input_values: torch.Tensor,
    input_indices: torch.Tensor,
    weight: torch.Tensor,
) -> torch.Tensor:
    """Return sparse output from matmul of sparse input and dense weight.

    Consider the batch matmul `einsum('...BMN, BNK -> ...BMK', in0, in1)`. For
    `in0`, if the dim `B` is sparse with only `b` values present, we can
    accelerate it with this function. The sparse representation of `in0` would
    be `in0_values` of shape (..., b, M, N) and `in0_indices` of shape (..., b,
    N, K). The relation between them is,
        ```
        in0 = torch.scatter(zeros, -3, in0_broadcasted_indices, in0_values))
        ```
    where in0_broadcasted_indices is in0_indices broadcasted to in0_values
    shape. Similarly the full dense output can be got from,
        ```
        out = torch.scatter(zeros, -3, out_broadcasted_indices, out_values))
        ```
    where out_broadcasted_indices is in0_indices broadcasted to out_values shape.

    Note the expected layout of `input` and `weight` are different from `in0`
    and `in1` used for explanation.

    Requires `input_indices` to fit in uint16 tensor.

    Args:
        input_values: Sparse input values.
        input_indices: Sparse input indices.
        weight: Dense weight.

    Returns:
        output_values: Sparse output values.

    Shapes:
        input_values: (..., M, compressed_sparse_dim, N)
        input_indices: (..., M, compressed_sparse_dim)
        weight: (K, full_sparse_dim, N)
        output_values: (..., M, compressed_sparse_dim, K)
    """
    if weight.size(1) >= 2**16:
        raise NotImplemented("Requires `input_indices` to fit in uint16 tensor")

    if cstorch.use_cs():
        return CSXSparseMatMul.apply(input_values, input_indices, weight)

    sparse_dim = -2
    compressed_sparse_dim_size = input_values.shape[sparse_dim]
    full_sparse_dim_size = weight.shape[sparse_dim]
    dense_input_shape = (
        *input_values.shape[:sparse_dim],
        full_sparse_dim_size,
        *input_values.shape[sparse_dim + 1 :],
    )
    indices = input_indices[..., None]

    # Scatter into dense input.
    dense_input = torch.zeros(
        dense_input_shape, dtype=input_values.dtype, device=input_values.device
    )
    dense_input.scatter_(
        sparse_dim, indices.broadcast_to(input_values.shape), input_values
    )

    output = torch.einsum("...MBN, KBN -> ...MBK", dense_input, weight)

    # Gather into sparse output.
    output_values_shape = (*input_values.shape[:-1], weight.shape[0])
    output_values = torch.gather(
        output, sparse_dim, indices.broadcast_to(output_values_shape)
    )
    return output_values
