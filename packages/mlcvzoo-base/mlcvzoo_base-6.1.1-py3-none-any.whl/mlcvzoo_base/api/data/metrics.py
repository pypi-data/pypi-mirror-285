# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

import logging

from shapely.errors import GEOSException
from shapely.geometry import Polygon

from mlcvzoo_base.api.data.box import GeometricPerception

logger = logging.getLogger(__name__)


def compute_iou(
    object_1: GeometricPerception,
    object_2: GeometricPerception,
) -> float:
    """
    Determine the Intersection-over-Union (IoU) of two objects

    Args:
        object_1: First object to compare
        object_2: Second object to compare

    Returns:
        The IoU between object_1 and object_2
    """

    iou: float

    try:
        gt_polygon = Polygon(object_1.polygon())
        polygon = Polygon(object_2.polygon())
        intersect = gt_polygon.intersection(polygon).area
        if intersect == 0.0:
            iou = 0.0
        else:
            union = gt_polygon.union(polygon).area
            iou = intersect / union
    except (ValueError, GEOSException):
        logger.exception("%s, return 0.0 IoU")
        iou = 0.0

    return iou
