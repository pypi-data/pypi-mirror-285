# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

""" Class for Bounding Box information"""

from __future__ import annotations

import logging
import math
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np

from mlcvzoo_base.api.data.types import (
    ImageType,
    Point2D,
    Point2f,
    PolygonType,
    PolygonTypeNP,
    point_equal,
)
from mlcvzoo_base.api.interfaces import Perception
from mlcvzoo_base.configuration.structs import ObjectDetectionBBoxFormats
from mlcvzoo_base.third_party.imutils.perspective import order_points

logger = logging.getLogger(__name__)


class GeometricPerception(ABC, Perception):
    @abstractmethod
    def box(self) -> Box:
        raise NotImplementedError(f"Call of .box() from abstract class {self.__class__}")

    @abstractmethod
    def ortho_box(self) -> Box:
        raise NotImplementedError(f"Call of .ortho_box() from abstract class {self.__class__}")

    @abstractmethod
    def polygon(self) -> PolygonTypeNP:
        raise NotImplementedError(f"Call of .polygon() from abstract class {self.__class__}")

    @staticmethod
    def polygon_to_rect_polygon(polygon: Union[PolygonType, PolygonTypeNP]) -> PolygonTypeNP:
        """
        Returns:
            The minimum orthogonal rectangular area around the polygon of this Segmentation
            represented as 4x2 numpy polygon.
        """

        return order_points(
            polygon=cv2.boxPoints(cv2.minAreaRect(np.asarray(polygon, dtype=np.int_))),
            sort_by_euclidean=False,
        )


class Box(GeometricPerception):
    """
    Class for storing bounding box information.

    The constructor is defined by the parameters upper left point and
    lower right point of the Box, as well as its rotation angle around the center
    of the Box. The points are defined as:
    - Upper left point given by xmin and ymin
    - Lower right point given by xmax and xmax
    |-----------------------|
    |(xmin, ymin)           |
    |                       |
    |                       |
    |          x angle      |
    |                       |
    |                       |
    |           (xmax, ymax)|
    |-----------------------|

    To avoid confusion a modulo operator is applied to the angle, which limits
    the angle value between 0 and 360 degrees.

    The width is determined between the top-left and top-right point.
    The height is determined between the top-left and bottom-left point.

    Internal representation of a Box is defined by its four points:
    - top-left
    - top-right
    - bottom-right
    - bottom-left

      ---       width       ---
      top-left        top-right
      |-----------------------|
      |X                     X|
      |                       |
      |                       |
      |                       |
      |                       |
      |                       |
      |X                     X|
      |-----------------------|
      bottom-left  bottom-right

      REMARK: The attributes xmin, ymin, xmax and ymax are not changed by the rotation and
            always reflect the original coordinates from the orthogonal box. For accessing
            the rotation points, please use top-left, top-right, bottom-right and bottom-left
    """

    def __init__(
        self, xmin: float, ymin: float, xmax: float, ymax: float, angle: float = 0.0
    ) -> None:
        """Creates a Box object

        Args:
            xmin: Upper left x coordinate of the Box
            ymin: Upper left y coordinate of the Box
            xmax: Lower right x coordinate of the Box
            ymax: Lower right y coordinate of the Box
            angle: Rotation angle in degrees around the
                   center point of the Box.

        Returns:
            The created object
        """
        if xmin >= xmax:
            raise ValueError(f"xmin={xmin} has to be < xmax={xmax}")

        if ymin >= ymax:
            raise ValueError(f"ymin={ymin} has to be < ymax={ymax}")

        self._angle: float = angle % 360

        self._xmin: float = float(xmin)
        self._ymin: float = float(ymin)
        self._xmax: float = float(xmax)
        self._ymax: float = float(ymax)

        self._point_0 = [self._xmin, self._ymin]
        self._point_1 = [self._xmax, self._ymin]
        self._point_2 = [self._xmax, self._ymax]
        self._point_3 = [self._xmin, self._ymax]

        self._center: Point2f = self.__center()

        self.__update()

    def __eq__(self, other: object) -> bool:
        try:
            return (
                point_equal(self._point_0, other._point_0)  # type: ignore[attr-defined]
                and point_equal(self._point_1, other._point_1)  # type: ignore[attr-defined]
                and point_equal(self._point_2, other._point_2)  # type: ignore[attr-defined]
                and point_equal(self._point_3, other._point_3)  # type: ignore[attr-defined]
            )
        except AttributeError:
            return False

    def __repr__(self) -> str:
        return (
            f"Box("
            f"xmin={self._xmin}, "
            f"ymin={self._ymin}, "
            f"xmax={self._xmax}, "
            f"ymax={self._ymax}, "
            f"angle={self._angle}"
            f")"
        )

    def to_dict(self) -> Dict[str, float]:
        return {
            "xmin": self._xmin,
            "ymin": self._ymin,
            "xmax": self._xmax,
            "ymax": self._ymax,
            "angle": self._angle,
        }

    def to_json(self) -> Any:
        return self.to_dict()

    def __update(self) -> None:
        if self._angle != 0.0:
            four_point_box = cv2.boxPoints(
                (self._center, (self._xmax - self._xmin, self._ymax - self._ymin), self._angle)
            )
            four_point_box = order_points(polygon=four_point_box, sort_by_euclidean=False)
            # Cast to convert numpy to python int
            self._point_0 = [float(four_point_box[0][0]), float(four_point_box[0][1])]
            self._point_1 = [float(four_point_box[1][0]), float(four_point_box[1][1])]
            self._point_2 = [float(four_point_box[2][0]), float(four_point_box[2][1])]
            self._point_3 = [float(four_point_box[3][0]), float(four_point_box[3][1])]
        else:
            self._point_0 = [self._xmin, self._ymin]
            self._point_1 = [self._xmax, self._ymin]
            self._point_2 = [self._xmax, self._ymax]
            self._point_3 = [self._xmin, self._ymax]

        self._center = self.__center()

    @property
    def xmin(self) -> int:
        return int(self._xmin)

    @property
    def ymin(self) -> int:
        return int(self._ymin)

    @property
    def xmax(self) -> int:
        return int(self._xmax)

    @property
    def ymax(self) -> int:
        return int(self._ymax)

    @property
    def xminf(self) -> float:
        return self._xmin

    @property
    def yminf(self) -> float:
        return self._ymin

    @property
    def xmaxf(self) -> float:
        return self._xmax

    @property
    def ymaxf(self) -> float:
        return self._ymax

    @property
    def angle(self) -> float:
        return self._angle

    @property
    def width(self) -> int:
        return int(self.widthf)

    @property
    def height(self) -> int:
        return int(self.heightf)

    @property
    def widthf(self) -> float:
        if self.is_orthogonal():
            return abs(self.top_left[0] - self.top_right[0])

        return float(
            math.sqrt(
                math.pow(self.top_left[0] - self.top_right[0], 2)
                + math.pow(self.top_left[1] - self.top_right[1], 2)
            )
        )

    @property
    def heightf(self) -> float:
        if self.is_orthogonal():
            return abs(self.top_left[1] - self.bottom_left[1])

        return float(
            math.sqrt(
                math.pow(self.top_left[0] - self.bottom_left[0], 2)
                + math.pow(self.top_left[1] - self.bottom_left[1], 2)
            )
        )

    @property
    def top_left(self) -> Point2f:
        return self._point_0

    @property
    def top_right(self) -> Point2f:
        return self._point_1

    @property
    def bottom_right(self) -> Point2f:
        return self._point_2

    @property
    def bottom_left(self) -> Point2f:
        return self._point_3

    @property
    def top_left_2d(self) -> Point2D:
        return [int(self._point_0[0]), int(self._point_0[1])]

    @property
    def top_right_2d(self) -> Point2D:
        return [int(self._point_1[0]), int(self._point_1[1])]

    @property
    def bottom_right_2d(self) -> Point2D:
        return [int(self._point_2[0]), int(self._point_2[1])]

    @property
    def bottom_left_2d(self) -> Point2D:
        return [int(self._point_3[0]), int(self._point_3[1])]

    def is_orthogonal(self) -> bool:
        return self._angle % 90 == 0.0

    @staticmethod
    def init_format_based(
        box_format: str,
        box_list: Tuple[float, float, float, float],
        src_shape: Optional[Tuple[int, int]] = None,
        dst_shape: Optional[Tuple[int, int]] = None,
        angle: float = 0.0,
    ) -> Box:
        """
        Construct a Box object using the given format and box coordinates

        Args:
            box_format: Specify the way for parsing the box argument
            box_list: The box coordinates as 4D tuple
            src_shape: shape of the original image as tuple (height, width)
            dst_shape: desired shape for creating the bounding boxes as tuple (height, width)
            angle: The rotation angle around the center of the box in degrees

        Returns:
            The constructed Box object
        """

        xmin = max(0.0, box_list[0])
        ymin = max(0.0, box_list[1])

        width = box_list[2]
        if width < 0:
            raise ValueError("Can not build a box with negative width")

        height = box_list[3]
        if height < 0:
            raise ValueError("Can not build a box with negative height")

        if box_format == ObjectDetectionBBoxFormats.XYWH:
            base_box = Box(
                xmin=xmin,
                ymin=ymin,
                xmax=xmin + width,
                ymax=ymin + height,
                angle=angle,
            )
        elif box_format == ObjectDetectionBBoxFormats.XYXY:
            base_box = Box(xmin=xmin, ymin=ymin, xmax=width, ymax=height, angle=angle)
        elif box_format == ObjectDetectionBBoxFormats.CXCYWH:
            base_box = Box(
                xmin=(xmin - width / 2),
                ymin=(ymin - height / 2),
                xmax=(xmin + width / 2),
                ymax=(ymin + height / 2),
                angle=angle,
            )
        else:
            valid_formats = ObjectDetectionBBoxFormats.get_values_as_list(
                class_type=ObjectDetectionBBoxFormats
            )
            raise ValueError(
                f"Format {box_format} is not supported. Please provide any of {valid_formats}"
            )

        if src_shape is not None:
            base_box.clamp(shape=src_shape)

        if src_shape is not None and dst_shape is not None:
            base_box.scale(src_shape=src_shape, dst_shape=dst_shape)

        return base_box

    @staticmethod
    def from_polygon(polygon: Union[PolygonType, PolygonTypeNP], orthogonal: bool = True) -> Box:
        """
        Produce a box object that covers the minimal rectangular area which is
        covered by the given polygon. When the parameter 'orthogonal' is set to true,
        the box will be orthogonal, otherwise a rotated box will be created.

        Args:
            polygon: PolygonType, a list of points that form the polygon
            orthogonal: Whether the created box should be orthogonal or can be rotated

        Returns:
            A Box that holds the coordinates of the bounding rectangle of the polygon
        """

        if orthogonal:
            x, y, w, h = cv2.boundingRect(np.asarray(polygon, dtype=np.int_))

            return Box.init_format_based(
                box_list=(
                    float(x),
                    float(y),
                    float(w),
                    float(h),
                ),
                box_format=ObjectDetectionBBoxFormats.XYWH,
            )

        (x, y), (w, h), angle = cv2.minAreaRect(np.asarray(polygon, dtype=np.int_))

        return Box.init_format_based(
            box_format=ObjectDetectionBBoxFormats.CXCYWH,
            box_list=(int(x), int(y), int(w), int(h)),
            angle=angle,
        )

    def to_list(self, dst_type: Any = int) -> List[Any]:
        """
        Args:
            dst_type: destination type to transform the data to

        Returns:
            List of transformed polygons
        """

        return [
            dst_type(self._xmin),
            dst_type(self._ymin),
            dst_type(self._xmax),
            dst_type(self._ymax),
        ]

    def box(self) -> Box:
        """Creates a copy of this Box object

        Returns:
            The created Box object
        """
        return Box(
            xmin=self._xmin, ymin=self._ymin, xmax=self._xmax, ymax=self._ymax, angle=self._angle
        )

    def ortho_box(self) -> Box:
        """The orthogonal box around this Box object. In case of an already orthogonal
        Box, the same instance is returned, otherwise a (orthogonal) box around the polygon of
        the Box object is created.

        Returns:
            The orthogonal Box object
        """
        if self.is_orthogonal():
            return self.box()

        return Box.from_polygon(polygon=self.polygon(), orthogonal=True)

    def polygon(self) -> PolygonTypeNP:
        return np.asarray(
            [
                self.top_left,
                self.top_right,
                self.bottom_right,
                self.bottom_left,
            ]
        )

    def clamp(self, shape: Tuple[int, int]) -> None:
        """
        Clamps the bounding-box based on the given shape

        Does only work for orthogonal boxes.

        Args:
            shape: The shape to define the min and max coordinates
                   for the clamping, format in (y, x)

        Returns:
            None
        """

        self._xmin = max(0.0, self._xmin)
        self._ymin = max(0.0, self._ymin)
        self._ymax = min(float(shape[0] - 1), self._ymax)
        self._xmax = min(float(shape[1] - 1), self._xmax)

        self.__update()

    def scale(self, src_shape: Tuple[int, int], dst_shape: Tuple[int, int]) -> None:
        """
        Scale the Box according to the given shapes of the source and destination image

        Args:
            src_shape: shape of the original image as tuple (height, width)
            dst_shape: desired shape for creating the bounding boxes as tuple (height, width)

        Returns:
            None
        """
        if src_shape[0] < 0 or src_shape[1] < 0 or src_shape[0] > src_shape[1]:
            raise ValueError("Invalid source shape %s: ", src_shape)

        if dst_shape[0] < 0 or dst_shape[1] < 0 or dst_shape[0] > dst_shape[1]:
            raise ValueError("Invalid destination shape %s: ", dst_shape)

        height_scale_factor = dst_shape[0] / src_shape[0]
        width_scale_factor = dst_shape[1] / src_shape[1]

        self._xmin = self.xmin * width_scale_factor
        self._xmax = self.xmax * width_scale_factor
        self._ymin = self.ymin * height_scale_factor
        self._ymax = self.ymax * height_scale_factor

        self.__update()

    def center(self) -> Point2f:
        """
        Calculates the geometric center of the Box

        Returns:
            A Tuple as the coordinates of the center
        """
        return self._center

    def __center(self) -> Point2f:
        """
        Calculates the center coordinates of the Box

        Returns:
            A Tuple as the coordinates of the center
        """
        return [
            (self._point_0[0] + self._point_2[0]) * 0.5,
            (self._point_0[1] + self._point_2[1]) * 0.5,
        ]

    def translation(self, x: float, y: float) -> None:
        """
        Shifts Box for x and y pixels in x and y direction respectively

        Args:
            x: int value for shift in x direction
            y: int value for shift in y direction

        Returns:
            None
        """
        self._xmin += x
        self._xmax += x
        self._ymin += y
        self._ymax += y

        self.__update()

    def new_center(self, x: float, y: float) -> None:
        """
        Shifts the Box based on a new center coordinate. Scale of Box is kept.

        Args:
            x: int value, x coordinate of the new center
            y: int value, y coordinate of the new center

        Returns:
            None
        """
        self.translation(x=x - self.center()[0], y=y - self.center()[1])

    def crop_img(
        self, frame: ImageType, margin_x: float = 0.0, margin_y: float = 0.0
    ) -> Optional[ImageType]:
        """
        Create a crop of the given frame based on the information of this box object
        and the given margins. The margin are used as scale factors based on the
        width (x direction) and height (y-direction)

        Args:
            frame: The frame to crop from
            margin_x: The margin around the box in x direction
            margin_y: The margin around the box in y direction

        Returns:
            The cropped image (if it could be computed)
        """

        if frame is None:
            return None

        box = self.ortho_box()

        xmin = box.xmin - round(margin_x * box.width)
        xmax = box.xmax + round(margin_x * box.width)
        ymin = box.ymin - round(margin_y * box.height)
        ymax = box.ymax + round(margin_y * box.height)

        margin_box = Box(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
        margin_box.clamp(shape=(frame.shape[0], frame.shape[1]))

        cropped_image = frame[
            int(margin_box.ymin) : int(margin_box.ymax),
            int(margin_box.xmin) : int(margin_box.xmax),
        ]

        return cropped_image

    def color_hist(
        self,
        frame: ImageType,
        margin_x: float,
        margin_y: float,
    ) -> Optional[ImageType]:
        """
        Calculate the color history the for the Box. First a crop
        of the given image is created based on the box information
        of this object and the given margins. The margin are used
        as scale factors based on the width (x direction) and height
        (y-direction).
        Afterwards the histogram is computed for this crop.

        Args:
            frame: The frame to crop from
            margin_x: The margin around the box in x direction
            margin_y: The margin around the box in y direction

        Returns:
            Color histogram of the box
        """

        cropped_image = self.crop_img(frame=frame, margin_x=margin_x, margin_y=margin_y)

        if cropped_image is None:
            return None

        # Convert image to HSV (Hue, Saturation, Value)
        hsv_image: ImageType = cv2.cvtColor(  # pylint: disable=no-member
            cropped_image, cv2.COLOR_BGR2HSV  # pylint: disable=no-member
        )

        h_bins = 10
        s_bins = 10

        # hue varies from 0 to 179, saturation from 0 to 255
        h_ranges = [0, 180]
        s_ranges = [0, 256]

        # Use the 0-th and 1-st channels
        channels = [0, 1]
        color_hist: ImageType = cv2.calcHist(
            [hsv_image],
            channels,
            None,
            [h_bins, s_bins],
            h_ranges + s_ranges,
            accumulate=False,
        )
        cv2.normalize(color_hist, color_hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

        return color_hist


def compute_iou(box_1: Box, box_2: Box) -> float:
    """
    Determine the Intersection-over-Union (IoU) of two box objects

    IMPORTANT: This method in designed for orthogonal boxes. Therefore,
               the iou is based on the ortho_box of each box object

    Args:
        box_1: Box object 1
        box_2: Box object 2

    Returns:
        The IoU between box_1 and box_2
    """

    # Ensure to have orthogonal boxes!
    box_1 = box_1.ortho_box()
    box_2 = box_2.ortho_box()

    # Determine the coordinates of the intersection rectangle
    x_left = max(box_1.xmin, box_2.xmin)
    x_right = min(box_1.xmax, box_2.xmax)
    y_bottom = min(box_1.ymax, box_2.ymax)
    y_top = max(box_1.ymin, box_2.ymin)

    # Boxes don't overlap at all
    if x_right < x_left or y_bottom < y_top:
        return 0.0

    # The intersection of two axis-aligned bounding boxes
    # is always an axis-aligned bounding box => A(intersect)
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # Compute the area of both boxes => A(box_1) and A(box_2(
    box_1_area = (box_1.xmax - box_1.xmin) * (box_1.ymax - box_1.ymin)
    box_2_area = (box_2.xmax - box_2.xmin) * (box_2.ymax - box_2.ymin)

    # Compute the intersection over union by taking the intersection
    # area and dividing it by the sum of box areas:
    # => iou = A(intersect) / ( A(box_1) + A(box_2))
    iou = intersection_area / float(box_1_area + box_2_area - intersection_area)

    # Clamp the iou value
    return max(min(iou, 1.0), 0.0)


def euclidean_distance(box_1: Box, box_2: Box) -> float:
    """
    Determine the euclidean distance between two Box objects

    Args:
        box_1: Box object 1
        box_2: Box object 2

    Returns:
        The euclidean distance between two Box objects
    """

    center1 = box_1.center()
    center2 = box_2.center()

    return float(((center2[0] - center1[0]) ** 2 + (center2[1] - center1[1]) ** 2) ** 0.5)


def rotate_point(point: Point2f, rotation_origin: Point2f, angle: float) -> Point2f:
    """
    Rotate a given point around an origin point with a given angle

    Args:
        point: The point to rotate
        rotation_origin: The origin point around which the point is rotated
        angle: The rotation angle

    Returns:
        The rotated point
    """
    x0 = rotation_origin[0]
    x1 = point[0]

    y0 = rotation_origin[1]
    y1 = point[1]

    rad_angle = angle * (math.pi / 180)

    x2 = ((x1 - x0) * math.cos(rad_angle)) - ((y1 - y0) * math.sin(rad_angle)) + x0
    y2 = ((x1 - x0) * math.sin(rad_angle)) + ((y1 - y0) * math.cos(rad_angle)) + y0

    return [float(x2), float(y2)]
