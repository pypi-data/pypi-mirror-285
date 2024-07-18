# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""Module for runtimes options."""

from typing import Final

float_equality_precision: Final[float] = 1e-5


class Runtime:
    """Class holding all runtimes a model can be converted to."""

    DEFAULT = "DEFAULT"
    ONNXRUNTIME = "ONNXRUNTIME"
    ONNXRUNTIME_FLOAT16 = "ONNXRUNTIME_FLOAT16"
    TENSORRT = "TENSORRT"
    TENSORRT_INT8 = "TENSORRT_INT8"
