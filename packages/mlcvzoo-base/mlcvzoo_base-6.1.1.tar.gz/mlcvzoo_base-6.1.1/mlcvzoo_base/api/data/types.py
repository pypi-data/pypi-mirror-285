# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""
Module for storing types that are shared across the mlcvzoo
"""

from __future__ import annotations

from math import isclose
from typing import List, NamedTuple, Sequence, Union

import numpy as np

from mlcvzoo_base.api.structs import float_equality_precision

try:
    from typing import Literal

    from numpy.typing import NDArray
    from typing_extensions import Annotated

    ImageType = Annotated[NDArray[np.int_], Literal["Height", "Width", 3]]
    PolygonTypeNP = Annotated[NDArray[np.float_], Literal["Length", 2]]
    Point2fNP = Annotated[NDArray[np.float_], Literal[1, 2]]
    Point2DNP = Annotated[NDArray[np.int_], Literal[1, 2]]
except ImportError as import_error:
    # NDArray is available from numpy>=1.21.0
    ImageType = np.ndarray  # type: ignore[misc]
    PolygonTypeNP = np.ndarray  # type: ignore[misc]
    Point2fNP = np.ndarray  # type: ignore[misc]
    Point2DNP = np.ndarray  # type: ignore[misc]


# Point as [x, y]
Point2f = Sequence[float]
Point2D = Sequence[int]
PolygonType = List[Point2f]


class FrameShape(NamedTuple):
    height: int
    width: int
    channel: int = 3


def point_equal(point: Point2f, other_point: Point2f) -> bool:
    """
    Args:
        point: The first point to compare
        other_point: The second point to compare

    Returns:
         Whether the two given points are equal
    """
    return isclose(a=point[0], b=other_point[0], abs_tol=float_equality_precision) and isclose(
        a=point[1], b=other_point[1], abs_tol=float_equality_precision
    )


def polygon_equal(
    polygon: Union[PolygonType, PolygonTypeNP], other_polygon: Union[PolygonType, PolygonTypeNP]
) -> bool:
    """
    Args:
        polygon: The first polygon to compare
        other_polygon: The second polygon to compare

    Returns:
         Whether the two given polygons are equal
    """
    if len(polygon) == len(other_polygon):
        for polygon_point, other_polygon_point in zip(polygon, other_polygon):
            if not point_equal(point=polygon_point, other_point=other_polygon_point):
                return False
    else:
        return False

    return True
