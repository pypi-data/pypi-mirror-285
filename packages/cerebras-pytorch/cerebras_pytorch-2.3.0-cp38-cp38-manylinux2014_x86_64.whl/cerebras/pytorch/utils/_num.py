# Copyright 2016-2023 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

""" Common numerics related utility functions """


def ceildiv(a, b):
    """Returns the ceiling of a/b"""
    q, r = divmod(a, b)
    return q + bool(r)
