# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

""" Class for Segmentation (polygon areas) annotations"""
from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np

from mlcvzoo_base.api.data.annotation_attributes import AnnotationAttributes
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.data.classification import Classification
from mlcvzoo_base.api.data.geometric_classifiction import GeometricClassification
from mlcvzoo_base.api.data.types import PolygonType, PolygonTypeNP, polygon_equal
from mlcvzoo_base.api.structs import float_equality_precision


class Segmentation(GeometricClassification, AnnotationAttributes):
    """
    A class for defining the data object consumed by Segmentation models.
    It is mainly described by its polygon (list of 2D points) attribute.
    The polygon captures an area of the image, that is defined by the
    inner of the linear connected points of the polygon and is associated
    with a certain class.
    In addition, a segmentation CAN have an attribute "box" that defines the rectangle
    which encloses the area of the polygon.
    """

    def __init__(
        self,
        polygon: Union[PolygonType, PolygonTypeNP],
        class_identifier: ClassIdentifier,
        score: float,
        difficult: bool = False,
        occluded: bool = False,
        content: str = "",
        model_class_identifier: Optional[ClassIdentifier] = None,
        background: bool = False,
        meta_attributes: Optional[Dict[Any, Any]] = None,
    ):
        Classification.__init__(
            self,
            class_identifier=class_identifier,
            model_class_identifier=model_class_identifier,
            score=score,
        )
        AnnotationAttributes.__init__(
            self,
            difficult=difficult,
            occluded=occluded,
            background=background,
            content=content,
            meta_attributes=meta_attributes,
        )
        self.__polygon: PolygonTypeNP = np.asarray(polygon)

        # The boxes are created lazily
        self.__box: Optional[Box] = None
        self.__ortho_box: Optional[Box] = None

    def polygon(self) -> PolygonTypeNP:
        return self.__polygon

    def ortho_box(self) -> Box:
        if self.__ortho_box is None:
            self.__ortho_box = Box.from_polygon(polygon=self.polygon(), orthogonal=True)
        return self.__ortho_box

    def box(self) -> Box:
        if self.__box is None:
            self.__box = Box.from_polygon(polygon=self.polygon(), orthogonal=False)
        return self.__box

    def __eq__(self, other: object) -> bool:
        try:
            # NOTE: Since floats may very for different systems, don't check the score for equality,
            #       but allow it to be in a reasonable range
            return (
                self.class_identifier.class_id == other.class_identifier.class_id  # type: ignore[attr-defined]
                and self.class_identifier.class_name == other.class_identifier.class_name  # type: ignore[attr-defined]
                and self.model_class_identifier.class_id
                == other.model_class_identifier.class_id  # type: ignore[attr-defined]
                and self.model_class_identifier.class_name
                == other.model_class_identifier.class_name  # type: ignore[attr-defined]
                and self.occluded == other.occluded  # type: ignore[attr-defined]
                and self.difficult == other.difficult  # type: ignore[attr-defined]
                and self.background == other.background  # type: ignore[attr-defined]
                and self.content == other.content  # type: ignore[attr-defined]
                and self.meta_attributes == other.meta_attributes  # type: ignore[attr-defined]
                and math.isclose(a=self.score, b=other.score, abs_tol=float_equality_precision)  # type: ignore[attr-defined]
                and self.box() == other.box()  # type: ignore[attr-defined]
                and polygon_equal(polygon=self.polygon(), other_polygon=other.polygon())  # type: ignore[attr-defined]
            )
        except AttributeError:
            return False

    def __str__(self):  # type: ignore
        return (
            f"Segmentation("
            f'class_identifier="{str(self.class_identifier)}", '
            f'model_class_identifier="{str(self.model_class_identifier)}", '
            f"polygon={self.__polygon.tolist()}, "
            f"score={self.score}, "
            f"difficult={self.difficult}, "
            f"occluded={self.occluded}, "
            f"background={self.background}, "
            f'content="{self.content}", '
            f"meta_attributes={self.meta_attributes}"
            f")"
        )

    def __repr__(self):  # type: ignore
        return (
            f"Segmentation("
            f"class_identifier={repr(self.class_identifier)}, "
            f"model_class_identifier={repr(self.model_class_identifier)}, "
            f"polygon={self.__polygon.tolist()}, "
            f"score={self.score}, "
            f"difficult={self.difficult}, "
            f"occluded={self.occluded}, "
            f"background={self.background}, "
            f'content="{self.content}", '
            f"meta_attributes={self.meta_attributes}"
            f")"
        )

    def to_dict(self, raw_type: bool = False, reduced: bool = False) -> Dict[str, Any]:
        """
        Generate a dictionary representation of the object. The raw_type defined whether
        all data attributes should be converted to python native data types or should
        be kept as is. The reduced parameter allows to create a more compact representation
        where only the main attributes of the object are present.

        Args:
            raw_type: Whether to convert the data attributes to python native data types
            reduced: Whether to create a more compact representation

        Returns:
            The created dictionary representation
        """
        if reduced:
            return {
                "polygon": self.__polygon if raw_type else self.__polygon.tolist(),
                "class_id": self.class_id,
                "class_name": self.class_name,
                "model_class_id": self.model_class_identifier.class_id,
                "model_class_name": self.model_class_identifier.class_name,
                "score": self.score,
            }

        return {
            "polygon": self.__polygon if raw_type else self.__polygon.tolist(),
            "class_identifier": (
                self.class_identifier if raw_type else self.class_identifier.to_dict()
            ),
            "model_class_identifier": (
                self.model_class_identifier if raw_type else self.model_class_identifier.to_dict()
            ),
            "score": self.score,
            "difficult": self.difficult,
            "occluded": self.occluded,
            "background": self.background,
            "content": self.content,
        }

    @staticmethod
    def from_dict(input_dict: Dict[str, Any], reduced: bool = False) -> Segmentation:
        # fmt: off
        if reduced:
            return Segmentation(**{
                "polygon": input_dict["polygon"],
                "class_identifier": ClassIdentifier(**{
                    "class_id": input_dict["class_id"],
                    "class_name": input_dict["class_name"],
                }),
                "model_class_identifier": ClassIdentifier(**{
                    "class_id": input_dict["model_class_id"],
                    "class_name": input_dict["model_class_name"],
                }),
                "score": input_dict["score"],
                "difficult": False,
                "occluded": False,
                "background": False,
                "content": "",
            })
        else:
            return Segmentation(**{
                "polygon": input_dict["polygon"],
                "class_identifier": ClassIdentifier(
                    **input_dict["class_identifier"]
                ),
                "model_class_identifier": ClassIdentifier(
                    **input_dict["model_class_identifier"]
                ),
                "score": input_dict["score"],
                "difficult": input_dict["difficult"],
                "occluded": input_dict["occluded"],
                "background": input_dict["background"],
                "content": input_dict["content"],
            })
        # fmt: on

    def to_json(self) -> Any:
        return self.to_dict(raw_type=False)

    def to_bounding_box(self, image_shape: Optional[Tuple[int, int]] = None) -> BoundingBox:
        """
        Manually build the bounding box object which covers the rectangular area
        that is defined by the polygon attribute

        Returns:
            A Bounding Box version of this Segmentation instance
        """
        box = self.box()

        if image_shape is not None:
            box.clamp(shape=image_shape)

        return BoundingBox(
            class_identifier=self.class_identifier,
            model_class_identifier=self.model_class_identifier,
            score=self.score,
            box=box,
            difficult=self.difficult,
            occluded=self.occluded,
            background=self.background,
            content=self.content,
        )

    def to_points_string(self) -> str:
        """
        Returns:
            Sting, concatenation of the coordinates of polygon attribute
        """

        points_string = ""
        for i, point in enumerate(self.__polygon):
            if i < len(self.__polygon) - 1:
                points_string = (
                    points_string + str(float(point[0])) + "," + str(float(point[1])) + ";"
                )
            else:
                points_string = points_string + str(float(point[0])) + "," + str(float(point[1]))

        return points_string

    def to_rect_segmentation(self) -> Segmentation:
        return Segmentation(
            polygon=self.polygon_to_rect_polygon(polygon=self.polygon()),
            class_identifier=self.class_identifier,
            score=self.score,
            difficult=self.difficult,
            occluded=self.occluded,
            background=self.background,
            content=self.content,
            model_class_identifier=self.model_class_identifier,
        )

    def copy_segmentation(self, class_identifier: ClassIdentifier) -> Segmentation:
        return Segmentation(
            polygon=self.__polygon,
            class_identifier=class_identifier,
            score=self.score,
            difficult=self.difficult,
            occluded=self.occluded,
            background=self.background,
            content=self.content,
            model_class_identifier=self.model_class_identifier,
        )
